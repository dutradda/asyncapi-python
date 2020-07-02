import asyncio
import dataclasses
from typing import Any, Callable, Dict, Tuple

from broadcaster import Broadcast
from jsonschema import validate

from .entities import Specification
from .exceptions import (
    ChannelOperationNotFoundError,
    InvalidChannelError,
    OperationIdNotFoundError,
)


OperationsTypeHint = Dict[Tuple[str, str], Callable[..., Any]]


@dataclasses.dataclass
class AsyncApi:
    spec: Specification
    operations: OperationsTypeHint
    broadcast: Broadcast

    async def publish(self, channel_id: str, message: Dict[str, Any]) -> None:
        self.validate_message(channel_id, message)
        await self.broadcast.publish(channel=channel_id, message=message)

    async def listen(self, channel_id: str) -> None:
        try:
            operation_id = self.spec.channels[
                channel_id
            ].subscribe.operation_id
        except KeyError:
            raise InvalidChannelError(channel_id)

        if operation_id is None:
            raise ChannelOperationNotFoundError(channel_id)

        async with self.broadcast.subscribe(channel=channel_id) as subscriber:
            async for event in subscriber:
                self.validate_message(channel_id, event.message)

                try:
                    coro = self.operations[(channel_id, operation_id)](
                        event.message
                    )
                except KeyError:
                    raise OperationIdNotFoundError(operation_id)

                if asyncio.iscoroutine(coro):
                    await coro

    def validate_message(
        self, channel_id: str, message: Dict[str, Any]
    ) -> None:
        try:
            schema = self.spec.channels[channel_id].subscribe.message.payload
        except KeyError:
            raise InvalidChannelError(channel_id)

        validate(instance=message, schema=schema)
