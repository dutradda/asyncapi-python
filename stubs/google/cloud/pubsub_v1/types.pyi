from typing import List


class PubsubMessage:
    data: bytes


class ReceivedMessage:
    message: PubsubMessage
    ack_id: str


class PullResponse:
    received_messages: List[ReceivedMessage]
