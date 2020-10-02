from typing import Any, Dict, AsyncGenerator, AsyncContextManager


class Event:
    channel: str
    message: Any

    def __init__(self, channel: str, message: Any): ...


class Broadcast:
    _subscribers: Dict[str, Any]

    def __init__(self, url: str): ...

    async def publish(self, channel: str, message: str) -> None: ...

    def subscribe(
        self, channel: str
    ) -> AsyncContextManager[AsyncGenerator[Event, None]]: ...

    async def connect(self) -> None: ...

    async def disconnect(self) -> None: ...
