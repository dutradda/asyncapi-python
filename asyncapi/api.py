import asyncio
import dataclasses
import logging
from typing import Any, Callable, Dict, Tuple

import orjson
from broadcaster import Broadcast
from jsondaora import DeserializationError, asdataclass, dataclass_asjson

from .exceptions import (
    ChannelOperationNotFoundError,
    InvalidChannelError,
    InvalidMessageError,
    OperationIdNotFoundError,
)
from .specification_v2_0_0 import Operation, Specification


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
        if self.spec.channels is None:
            raise InvalidChannelError(channel_id)

        operation_id = self.subscribe_operation(channel_id).operation_id

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

                except Exception:
                    if not self.republish_error_messages:
                        raise

                    self.logger.exception(f"message={event.message[:100]}")
                    await self.publish(channel_id, payload)

    def subscribe_operation(self, channel_id: str) -> Operation:
        try:
            operation = self.spec.channels[channel_id].subscribe

            if operation is None:
                raise InvalidChannelError(channel_id)

        except KeyError:
            raise InvalidChannelError(channel_id)

        else:
            return operation

    def parse_message(self, channel_id: str, message: Any) -> Any:
        payload_type = self.payload_type(channel_id)

        if payload_type:
            if not isinstance(message, payload_type):
                raise InvalidMessageError(message, payload_type)

            return dataclass_asjson(message)

        return message

    def payload_type(self, channel_id: str) -> Any:
        operation = self.subscribe_operation(channel_id)

        if operation.message is None:
            return None

        return operation.message.payload


def task_callback(future: Any) -> None:
    future.result()
