import asyncio
import functools
import secrets
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FutureTimeoutError
from logging import Logger, getLogger
from typing import TYPE_CHECKING, Any, Dict, Tuple
from urllib.parse import urlparse

from broadcaster._backends.base import BroadcastBackend
from google.cloud import pubsub_v1
from google.cloud.pubsub_v1.types import PullResponse, ReceivedMessage

from asyncapi import (
    GCloudPubSubConsumerDisconnectError,
    GCloudPubSubPublishTimeoutError,
)

from .. import Event


if TYPE_CHECKING:
    AsyncFutureHint = asyncio.Future[PullResponse]
else:
    AsyncFutureHint = asyncio.Future


class GCloudPubSubBackend(BroadcastBackend):
    def __init__(
        self,
        url: str,
        bindings: Dict[str, str] = {},
        logger: Logger = getLogger(__name__),
    ):
        url_parsed = urlparse(url, scheme='gcloud-pubsub')
        self._project = url_parsed.netloc
        self._consumer_channels: Dict[str, str] = {}
        self._producer_channels: Dict[str, str] = {}
        self._channel_index = 0
        self._logger = logger
        self._set_consumer_config(bindings)
        self._disconnected = True
        self._executor = ThreadPoolExecutor(self._consumer_max_workers)

    async def connect(self) -> None:
        self._producer = pubsub_v1.PublisherClient()
        self._consumer = pubsub_v1.SubscriberClient()
        self._disconnected = False

    async def disconnect(self) -> None:
        self._disconnected = True
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
                raise GCloudPubSubPublishTimeoutError(
                    f'publish timeout; channel={channel}; '
                    f'message={message[:100]}...'
                )
            else:
                await self.publish(channel, message, retries_counter + 1)

    async def next_published(self) -> Event:
        (
            received_message,
            channel_id,
            pubsub_channel,
        ) = await self._pull_message_from_consumer()
        event = Event(channel_id, received_message.message.data.decode())

        if self._consumer_ack_messages:
            await self.wait_ack(received_message, pubsub_channel)
        else:
            event.context['ack_func'] = functools.partial(
                self.wait_ack, received_message, pubsub_channel,
            )

        return event

    async def _pull_message_from_consumer(
        self,
    ) -> Tuple[ReceivedMessage, str, str]:
        channel_index = (
            secrets.choice(range(len(self._consumer_channels)))
            if self._consumer_channels
            else 0
        )

        while not self._disconnected:
            channels = list(self._consumer_channels.items())

            if not len(channels):
                await asyncio.sleep(self._consumer_wait_time)
                continue

            if channel_index >= len(channels):
                channel_index = 0

            channel_id, pubsub_channel = channels[channel_index]
            pull_message_future: AsyncFutureHint
            pull_message_future = asyncio.get_running_loop().run_in_executor(  # type: ignore
                self._executor,
                functools.partial(
                    self._consumer.pull,
                    pubsub_channel,
                    max_messages=1,
                    return_immediately=True,
                ),
            )

            try:
                response = await asyncio.wait_for(
                    pull_message_future, self._consumer_pull_message_timeout
                )

            except asyncio.TimeoutError:
                channel_index += 1
                await asyncio.sleep(self._consumer_wait_time)
                continue

            else:
                if not response.received_messages:
                    channel_index += 1
                    await asyncio.sleep(self._consumer_wait_time)
                    continue

                await asyncio.sleep(self._pull_message_wait_time)
                return (
                    response.received_messages[0],
                    channel_id,
                    pubsub_channel,
                )

        raise GCloudPubSubConsumerDisconnectError()

    async def wait_ack(
        self,
        message: ReceivedMessage,
        pubsub_channel: str,
        retries_counter: int = 1,
    ) -> None:
        future = asyncio.get_running_loop().run_in_executor(
            self._executor,
            functools.partial(
                self._consumer.acknowledge, pubsub_channel, [message.ack_id],
            ),
        )

        try:
            await asyncio.wait_for(future, timeout=self._consumer_ack_timeout)
        except asyncio.TimeoutError:
            if retries_counter >= self._consumer_ack_retries:
                self._logger.warning(
                    f'ack timeout {self._consumer_ack_timeout}; '
                    f'message={message.message.data.decode()[:100]}...'
                )
            else:
                await self.wait_ack(
                    message, pubsub_channel, retries_counter + 1
                )
        except asyncio.CancelledError:
            self._logger.warning(
                'ack cancelled; '
                f'message={message.message.data.decode()[:100]}...'
            )

    def _set_consumer_config(self, bindings: Dict[str, str]) -> None:
        consumer_wait_time = 1.0
        consumer_ack_messages = False
        consumer_ack_timeout = 1.0
        consumer_ack_retries = 3
        consumer_pull_message_timeout = 1.0
        consumer_max_workers = 10
        publish_timeout = 5.0
        publish_retries = 3
        pull_message_wait_time = 0.1

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

            elif config_name == 'publish_timeout':
                publish_timeout = float(config_value)

            elif config_name == 'publish_retries':
                publish_retries = int(config_value)

            elif config_name == 'pull_message_wait_time':
                pull_message_wait_time = float(config_value)

        self._consumer_wait_time = consumer_wait_time
        self._consumer_ack_messages = consumer_ack_messages
        self._consumer_ack_timeout = consumer_ack_timeout
        self._consumer_ack_retries = consumer_ack_retries
        self._consumer_pull_message_timeout = consumer_pull_message_timeout
        self._consumer_max_workers = consumer_max_workers
        self._publish_timeout = publish_timeout
        self._publish_retries = publish_retries
        self._pull_message_wait_time = pull_message_wait_time
