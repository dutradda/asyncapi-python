import asyncio
import dataclasses
import functools
import logging
from typing import Any, Callable, Dict, Tuple


try:
    import orjson as json

    def dumps_decorator(func: Callable[..., bytes]) -> Callable[..., str]:
        @functools.wraps(func)
        def wrapper(obj: Any) -> str:
            return func(obj).decode()

        return wrapper

    def loads_decorator(func: Callable[[bytes], Any]) -> Callable[[str], Any]:
        @functools.wraps(func)
        def wrapper(json_str: str) -> Any:
            return func(json_str.encode())

        return wrapper

    json.dumps = dumps_decorator(json.dumps)  # type: ignore
    json.loads = loads_decorator(json.loads)  # type: ignore

except ImportError:
    import json  # type: ignore

from broadcaster import Broadcast
from jsonschema import ValidationError, validate

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
    republish_error_messages: bool = True
    logger: logging.Logger = logging.getLogger(__name__)

    async def publish(self, channel_id: str, message: Dict[str, Any]) -> None:
        self.validate_message(channel_id, message)
        await self.broadcast.connect()
        await self.broadcast.publish(
            channel=channel_id, message=json.dumps(message)  # type: ignore
        )

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
                try:
                    json_message = json.loads(event.message)
                    self.validate_message(channel_id, json_message)

                    coro = self.operations[(channel_id, operation_id)](
                        json_message
                    )

                    if asyncio.iscoroutine(coro):
                        await coro

                except ValidationError:
                    raise

                except json.JSONDecodeError:
                    raise

                except KeyError:
                    raise OperationIdNotFoundError(operation_id)

                except Exception as error:
                    if not self.republish_error_messages:
                        raise

                    self.logger.warning(
                        f'error={type(error).__name__}; '
                        f"message={event.message[:100]}"
                    )
                    await self.publish(channel_id, json_message)

    def validate_message(
        self, channel_id: str, message: Dict[str, Any]
    ) -> None:
        try:
            schema = self.spec.channels[channel_id].subscribe.message.payload
        except KeyError:
            raise InvalidChannelError(channel_id)

        validate(instance=message, schema=schema)
