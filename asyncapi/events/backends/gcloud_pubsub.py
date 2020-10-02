import asyncio
import functools
from concurrent.futures import Future, ThreadPoolExecutor
from concurrent.futures import TimeoutError as FutureTimeoutError
from logging import Logger, getLogger
from typing import TYPE_CHECKING, Any, Dict, Optional
from urllib.parse import urlparse

from broadcaster._backends.base import BroadcastBackend
from google.cloud import pubsub_v1
from google.cloud.pubsub_v1.types import PullResponse, ReceivedMessage

from asyncapi import PublishTimeoutError

from .. import Event


if TYPE_CHECKING:
    FutureHint = Future[None]
else:
    FutureHint = Future


class GCloudPubSubBackend(BroadcastBackend):
    def __init__(
        self,
        url: str,
        bindings: Dict[str, str] = {},
        logger: Logger = getLogger(__name__),
        executor: Optional[ThreadPoolExecutor] = None,
    ):
        url_parsed = urlparse(url, scheme='gcloud-pubsub')
        self._project = url_parsed.netloc
        self._consumer_channels: Dict[str, str] = {}
        self._producer_channels: Dict[str, str] = {}
        self._channel_index = 0
        self._should_stop = True
        self._logger = logger
        self._set_consumer_config(bindings)

        if executor is None:
            executor = ThreadPoolExecutor(self._consumer_max_workers)

        self._executor = executor

    async def connect(self) -> None:
        self._producer = pubsub_v1.PublisherClient()
        self._consumer = pubsub_v1.SubscriberClient()
        self._should_stop = False

    async def disconnect(self) -> None:
        self._should_stop = True
        self._producer.stop()
        self._consumer.close()
        del self._producer
        del self._consumer

    async def subscribe(self, channel: str) -> None:
        pubsub_channel = self._consumer.subscription_path(
            self._project, channel
        )
        self._consumer_channels[channel] = pubsub_channel

    async def unsubscribe(self, channel: str) -> None:
        self._consumer_channels.pop(channel)

    async def publish(
        self, channel: str, message: Any, retries_counter: int = 1
    ) -> None:
        producer_channel = self._producer_channels.get(channel)

        if not producer_channel:
            producer_channel = self._producer.topic_path(
                self._project, channel
            )
            self._producer_channels[channel] = producer_channel

        future = self._producer.publish(producer_channel, message.encode())

        try:
            future.result(timeout=self._publish_timeout)
        except FutureTimeoutError:
            if retries_counter >= self._publish_retries:
                raise PublishTimeoutError(
                    f'publish timeout; channel={channel}; '
                    f'message={message[:100]}...'
                )
            else:
                await self.publish(channel, message, retries_counter + 1)

    async def next_published(self) -> Optional[Event]:
        channel_index = self._channel_index

        while not self._should_stop:
            channels = list(self._consumer_channels.items())

            if not channels:
                await asyncio.sleep(self._consumer_wait_time)
                continue

            channel_id, pubsub_channel = channels[channel_index]

            response = self._pull_message_from_consumer(pubsub_channel)

            if response is None or not response.received_messages:
                await asyncio.sleep(self._consumer_wait_time)
                if self._channel_index >= len(channels) - 1:
                    channel_index = self._channel_index = 0
                else:
                    self._channel_index += 1
                    channel_index = self._channel_index

            else:
                received_message = response.received_messages[0]
                event = Event(
                    channel_id, received_message.message.data.decode()
                )

                if self._consumer_ack_messages:
                    await self.wait_ack(received_message, pubsub_channel)
                else:
                    event.context['ack_func'] = functools.partial(
                        self.wait_ack, received_message, pubsub_channel,
                    )

                return event

        return None

    def _pull_message_from_consumer(
        self, pubsub_channel: str, retries_counter: int = 1,
    ) -> Optional[PullResponse]:
        future = self._executor.submit(
            self._consumer.pull,
            pubsub_channel,
            max_messages=1,
            return_immediately=True,
        )

        try:
            return future.result(timeout=self._consumer_pull_message_timeout)
        except FutureTimeoutError:
            if retries_counter >= self._consumer_pull_message_retries:
                self._logger.exception(
                    f'pull message timeout {self._consumer_pull_message_timeout}; '
                    f'channel={pubsub_channel}'
                )
                return None
            else:
                return self._pull_message_from_consumer(
                    pubsub_channel, retries_counter + 1
                )

    async def wait_ack(
        self,
        message: ReceivedMessage,
        pubsub_channel: str,
        retries_counter: int = 1,
    ) -> None:
        future = self._executor.submit(
            self._consumer.acknowledge, pubsub_channel, [message.ack_id],
        )

        try:
            future.result(timeout=self._consumer_ack_timeout)
        except FutureTimeoutError:
            if retries_counter >= self._consumer_ack_retries:
                self._logger.exception(
                    f'ack timeout; {message.message.data.decode()[:100]}...'
                )
            else:
                await self.wait_ack(
                    message, pubsub_channel, retries_counter + 1
                )

    def _set_consumer_config(self, bindings: Dict[str, str]) -> None:
        consumer_wait_time = 1.0
        consumer_ack_messages = False
        consumer_ack_timeout = 5.0
        consumer_ack_retries = 3
        consumer_max_workers = 10
        consumer_pull_message_timeout = 1.0
        consumer_pull_message_retries = 3
        publish_timeout = 5.0
        publish_retries = 3

        for config_name, config_value in bindings.items():
            if config_name == 'consumer_wait_time':
                consumer_wait_time = float(config_value)

            elif config_name == 'consumer_ack_messages':
                consumer_ack_messages = config_value in (
                    '1',
                    'true',
                    't',
                    'True',
                    'y',
                    'yes',
                )

            elif config_name == 'consumer_ack_timeout':
                consumer_ack_timeout = float(config_value)

            elif config_name == 'consumer_ack_retries':
                consumer_ack_retries = int(config_value)

            elif config_name == 'consumer_max_workers':
                consumer_max_workers = int(config_value)

            elif config_name == 'consumer_pull_message_timeout':
                consumer_pull_message_timeout = float(config_value)

            elif config_name == 'consumer_pull_message_retries':
                consumer_pull_message_retries = int(config_value)

            elif config_name == 'publish_timeout':
                publish_timeout = float(config_value)

            elif config_name == 'publish_retries':
                publish_retries = int(config_value)

        self._consumer_wait_time = consumer_wait_time
        self._consumer_ack_messages = consumer_ack_messages
        self._consumer_ack_timeout = consumer_ack_timeout
        self._consumer_ack_retries = consumer_ack_retries
        self._consumer_max_workers = consumer_max_workers
        self._consumer_pull_message_timeout = consumer_pull_message_timeout
        self._consumer_pull_message_retries = consumer_pull_message_retries
        self._publish_timeout = publish_timeout
        self._publish_retries = publish_retries
