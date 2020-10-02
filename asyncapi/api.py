import asyncio
import dataclasses
import logging
from typing import Any, Callable, Dict, Optional, Tuple, Type

import orjson
from jsondaora import DeserializationError, asdataclass, dataclass_asjson

from .events.handler import EventsHandler
from .exceptions import (
    ChannelOperationNotFoundError,
    ChannelPublishNotFoundError,
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
    events_handler: EventsHandler
    republish_error_messages: bool = False
    republish_error_messages_channels: Optional[Dict[str, str]] = None
    logger: logging.Logger = logging.getLogger(__name__)
    operation_timeout: Optional[int] = None

    async def publish_json(
        self, channel_id: str, message: Dict[str, Any]
    ) -> None:
        await self.events_handler.publish(
            channel=channel_id,
            message=self.parse_message(
                channel_id, self.payload(channel_id, **message)
            ).decode(),
        )

    async def publish(self, channel_id: str, message: Any) -> None:
        await self.events_handler.publish(
            channel=channel_id,
            message=self.parse_message(channel_id, message).decode(),
        )

    async def __aenter__(self) -> 'AsyncApi':
        await self.connect()
        return self

    async def __aexit__(self, *args: Any, **kwargs: Any) -> None:
        await self.disconnect()

    async def connect(self) -> None:
        await self.events_handler.connect()

    async def disconnect(self) -> None:
        await self.events_handler.disconnect()

    def payload(self, channel_id: str, **message: Any) -> Any:
        type_ = self.publish_payload_type(channel_id)
        return self.payload_type(type_, channel_id, **message)

    def subscriber_payload(self, channel_id: str, **message: Any) -> Any:
        type_ = self.subscribe_payload_type(channel_id)
        return self.payload_type(type_, channel_id, **message)

    def payload_type(
        self, type_: Type[Any], channel_id: str, **message: Any
    ) -> Any:
        if type_ and dataclasses.is_dataclass(type_):
            return asdataclass(message, type_)

        return message

    async def listen_all(self) -> None:
        tasks = []

        for channel_id, channel in self.spec.channels.items():
            if channel.subscribe:
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

        try:
            operation_func = self.operations[(channel_id, operation_id)]
        except KeyError:
            raise OperationIdNotFoundError(channel_id, operation_id)

        async with self.events_handler.subscribe(
            channel=channel_id
        ) as subscriber:
            async for event in subscriber:
                try:
                    json_message = orjson.loads(event.message)
                    payload = self.subscriber_payload(
                        channel_id, **json_message
                    )

                    coro = operation_func(
                        payload, **getattr(event, 'context', {})
                    )

                    if self.operation_timeout:
                        try:
                            while asyncio.iscoroutine(coro):
                                coro = await asyncio.wait_for(
                                    coro, timeout=self.operation_timeout
                                )
                        except asyncio.TimeoutError:
                            self.logger.exception(
                                f'operation timeout: {self.operation_timeout}; '
                                f'message={event.message[:100]}'
                            )
                    else:
                        while asyncio.iscoroutine(coro):
                            coro = await coro

                except (orjson.JSONDecodeError, DeserializationError):
                    self.logger.exception(f"message={event.message[:100]}")

                except Exception:
                    self.logger.exception(f"message={event.message[:100]}")

                    if self.republish_error_messages:
                        republish_channel = (
                            self.republish_error_messages_channels.get(
                                channel_id, channel_id
                            )
                            if self.republish_error_messages_channels
                            is not None
                            else channel_id
                        )

                        try:
                            await self.publish(republish_channel, payload)
                        except UnboundLocalError:
                            await self.publish_json(
                                republish_channel, json_message
                            )
                        except Exception:
                            self.logger.exception(
                                f"message={event.message[:100]}"
                            )

    def publish_operation(self, channel_id: str) -> Operation:
        return self.operation('publish', channel_id)

    def subscribe_operation(self, channel_id: str) -> Operation:
        return self.operation('subscribe', channel_id)

    def operation(self, op_name: str, channel_id: str) -> Operation:
        operation: Operation

        try:
            operation = getattr(self.spec.channels[channel_id], op_name)

            if operation is None:
                raise ChannelPublishNotFoundError(channel_id)

        except KeyError:
            raise InvalidChannelError(channel_id)

        else:
            return operation

    def parse_message(self, channel_id: str, message: Any) -> Any:
        type_ = self.publish_payload_type(channel_id)

        if type_:
            if not isinstance(message, type_):
                raise InvalidMessageError(message, type_)

            return dataclass_asjson(message)

        return message

    def publish_payload_type(self, channel_id: str) -> Any:
        operation = self.publish_operation(channel_id)

        if operation.message is None:
            return None

        return operation.message.payload

    def subscribe_payload_type(self, channel_id: str) -> Any:
        operation = self.subscribe_operation(channel_id)

        if operation.message is None:
            return None

        return operation.message.payload


def task_callback(future: Any) -> None:
    future.result()
