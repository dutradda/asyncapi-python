from .base import BroadcastBackend


class Client:
    async def close(self) -> None: ...


class Consumer:
    _client: Client

    def unsubscribe(self) -> None: ...

    async def stop(self) -> None: ...


class Producer:
    async def stop(self) -> None: ...


class KafkaBackend(BroadcastBackend):
    _consumer: Consumer
    _producer: Consumer

    def __init__(self, url: str): ...
