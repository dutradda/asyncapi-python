from typing import List, Any
from concurrent.futures import Future


class PublisherClient:
    def topic_path(self, project: str, topic: str) -> str: ...

    def publish(self, topic: str, message: bytes) -> Future[Any]: ...

    def stop(self) -> None: ...


class PubSubMessage:
    data: bytes


class PubSubResponse:
    message: PubSubMessage
    ack_id: str


class SubscriberResponse:
    received_messages: List[PubSubResponse]


class SubscriberClient:
    def subscription_path(self, project: str, subscription: str) -> str: ...

    def pull(
        self, subscription: str, max_messages: int, return_immediately: bool
    ) -> SubscriberResponse: ...

    def acknowledge(self, subscription: str, ids: List[str]) -> None: ...

    def close(self) -> None: ...
