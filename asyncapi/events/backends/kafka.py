from typing import Dict
from urllib.parse import urlparse

from broadcaster._backends.kafka import KafkaBackend as BroadcasterKafkaBackend


class KafkaBackend(BroadcasterKafkaBackend):
    def __init__(self, url: str, bindings: Dict[str, str] = {}):
        super().__init__(url)
        self._servers = urlparse(url).netloc.split(',')

    async def unsubscribe(self, channel: str) -> None:
        self._consumer.unsubscribe()
