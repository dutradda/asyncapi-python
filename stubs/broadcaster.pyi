from typing import Any, Dict, AsyncGenerator, AsyncContextManager


class Event:
    message: Dict[str,Any]


class Broadcast:
    def __init__(self, url: str): ...

    async def publish(self, channel: str, message: Dict[str, Any]) -> None: ...

    def subscribe(
        self, channel: str
    ) -> AsyncContextManager[AsyncGenerator[Event, None]]: ...
