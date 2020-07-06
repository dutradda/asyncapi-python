from typing import Any, Dict, AsyncGenerator, AsyncContextManager


class Event:
    message: str


class Broadcast:
    def __init__(self, url: str): ...

    async def publish(self, channel: str, message: str) -> None: ...

    def subscribe(
        self, channel: str
    ) -> AsyncContextManager[AsyncGenerator[Event, None]]: ...

    async def connect(self) -> None: ...
