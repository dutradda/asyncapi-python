import asyncio
import dataclasses
import logging
from typing import Any, Callable, Dict, Tuple

import orjson
from broadcaster import Broadcast
from jsondaora import DeserializationError, asdataclass, dataclass_asjson

from .entities import Specification
from .exceptions import (
    ChannelOperationNotFoundError,
    InvalidChannelError,
    InvalidMessageError,
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

    async def connect(self) -> None:
        await self.broadcast.connect()

    def payload(self, channel_id: str, **message: Any) -> Any:
        type_ = self.payload_type(channel_id)

        if type_ and dataclasses.is_dataclass(type_):
            return asdataclass(message, type_)

        return message

    async def publish_json(
        self, channel_id: str, message: Dict[str, Any]
    ) -> None:
        await self.broadcast.publish(
            channel=channel_id,
            message=self.parse_message(
                channel_id, self.payload(channel_id, **message)
            ).decode(),
        )

    async def publish(self, channel_id: str, message: Any) -> None:
        await self.broadcast.publish(
            channel=channel_id,
            message=self.parse_message(channel_id, message).decode(),
        )

    async def listen_all(self) -> None:
        tasks = []

        for channel_id in self.spec.channels.keys():
            task = asyncio.create_task(self.listen(channel_id))
            task.add_done_callback(task_callback)
            tasks.append(task)

        await asyncio.gather(*tasks)

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
                    json_message = orjson.loads(event.message)
                    payload = self.payload(channel_id, **json_message)

                    coro = self.operations[(channel_id, operation_id)](payload)

                    if asyncio.iscoroutine(coro):
                        await coro

                except (orjson.JSONDecodeError, DeserializationError):
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
                    await self.publish(channel_id, payload)

    def parse_message(self, channel_id: str, message: Any) -> Any:
        try:
            type_ = self.spec.channels[channel_id].subscribe.message.payload
        except KeyError:
            raise InvalidChannelError(channel_id)

        if type_:
            if not isinstance(message, type_):
                raise InvalidMessageError(message, type_)

            v = dataclass_asjson(message)
            return v

        return message

    def payload_type(self, channel_id: str) -> Any:
        try:
            return self.spec.channels[channel_id].subscribe.message.payload
        except KeyError:
            raise InvalidChannelError(channel_id)


def task_callback(future: Any) -> None:
    future.result()
