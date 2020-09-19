from .base import BroadcastBackend

class Consumer:
    def unsubscribe(self) -> None: ...


class KafkaBackend(BroadcastBackend):
    _consumer: Consumer

    def __init__(self, url: str): ...
