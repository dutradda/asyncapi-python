from .. import Event


class BroadcastBackend:
    async def next_published(self) -> Event: ...
