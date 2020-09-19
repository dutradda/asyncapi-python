import asyncio
import functools
from typing import Any, Dict, Optional
from urllib.parse import urlparse

from broadcaster._backends.base import BroadcastBackend
from google.cloud import pubsub_v1

from .. import Event


class GCloudPubSubBackend(BroadcastBackend):
    def __init__(self, url: str, bindings: Dict[str, str] = {}):
        url_parsed = urlparse(url, scheme='gcloud-pubsub')
        self._project = url_parsed.netloc
        self._consumer_channels: Dict[str, str] = {}
        self._producer_channels: Dict[str, str] = {}
        self._channel_index = 0
        self._should_stop = True
        self._set_consumer_config(bindings)

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

    async def publish(self, channel: str, message: Any) -> None:
        producer_channel = self._producer_channels.get(channel)

        if not producer_channel:
            producer_channel = self._producer.topic_path(
                self._project, channel
            )
            self._producer_channels[channel] = producer_channel

        future = self._producer.publish(producer_channel, message.encode())
        future.result()

    async def next_published(self) -> Optional[Event]:
        channel_index = self._channel_index

        while not self._should_stop:
            channels = list(self._consumer_channels.items())

            if not channels:
                await asyncio.sleep(self._consumer_wait_time)
                continue

            channel_id, pubsub_channel = channels[channel_index]

            response = self._consumer.pull(
                pubsub_channel, max_messages=1, return_immediately=True
            )

            if not response.received_messages:
                await asyncio.sleep(self._consumer_wait_time)
                if self._channel_index >= len(channels) - 1:
                    channel_index = self._channel_index = 0
                else:
                    self._channel_index += 1
                    channel_index = self._channel_index

            else:
                pubsub_response = response.received_messages[0]
                event = Event(
                    channel_id, pubsub_response.message.data.decode()
                )

                if self._consumer_ack_messages:
                    self._consumer.acknowledge(
                        pubsub_channel, [pubsub_response.ack_id]
                    )
                else:
                    event.context['ack_func'] = functools.partial(
                        self._consumer.acknowledge,
                        pubsub_channel,
                        [pubsub_response.ack_id],
                    )

                return event

        return None

    def _set_consumer_config(self, bindings: Dict[str, str]) -> None:
        consumer_wait_time = 1.0
        consumer_ack_messages = True

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

        self._consumer_wait_time = consumer_wait_time
        self._consumer_ack_messages = consumer_ack_messages
