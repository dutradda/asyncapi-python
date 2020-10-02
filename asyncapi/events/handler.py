import itertools
from typing import Any, Dict
from urllib.parse import urlparse

from broadcaster import Broadcast
from broadcaster._backends.base import BroadcastBackend

from ..exceptions import GCloudPubSubConsumerDisconnectError


class EventsHandler(Broadcast):
    _backend: BroadcastBackend

    def __init__(self, url: str, bindings: Dict[str, Any] = {}):
        super().__init__(url)

        parsed_url = urlparse(url)

        if parsed_url.scheme == 'kafka':
            from .backends.kafka import KafkaBackend

            self._backend = KafkaBackend(url, bindings)

        elif parsed_url.scheme == 'gcloud-pubsub':
            from .backends.gcloud_pubsub import GCloudPubSubBackend

            self._backend = GCloudPubSubBackend(url, bindings)

    async def _listener(self) -> None:
        while True:
            try:
                event = await self._backend.next_published()
            except GCloudPubSubConsumerDisconnectError:
                for queue in itertools.chain(*self._subscribers.values()):
                    queue.clear()
                    return
            else:
                for queue in list(self._subscribers.get(event.channel, [])):
                    await queue.put(event)
