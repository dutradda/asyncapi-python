import dataclasses
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


@dataclasses.dataclass
class Info:
    title: str
    version: str
    description: str


class ProtocolType(Enum):
    KAFKA = 'kafka'
    REDIS = 'redis'
    POSTGRES = 'postgres'


@dataclasses.dataclass
class Server:
    name: str
    url: str
    protocol: ProtocolType
    description: str


@dataclasses.dataclass
class Message:
    name: str
    title: str
    summary: str
    content_type: str
    payload: Any


@dataclasses.dataclass
class Subscribe:
    message: Message
    operation_id: Optional[str] = None


@dataclasses.dataclass
class Channel:
    name: str
    description: str
    subscribe: Subscribe


@dataclasses.dataclass
class Components:
    messages: Optional[Dict[str, Message]] = None
    schemas: Optional[Dict[str, Any]] = None


@dataclasses.dataclass
class Specification:
    info: Info
    servers: List[Server]
    channels: List[Channel]
    components: Optional[Components] = None
    default_content_type: Optional[str] = None


OperationsTypeHint = Dict[str, Dict[str, Callable[..., Any]]]


@dataclasses.dataclass
class AsyncApi:
    spec: Specification
    operations: OperationsTypeHint

    def __getattr__(self, attr_name: str, default_value: Any = None) -> Any:
        return self.operations.get(attr_name) or super().__getattr__(  # type: ignore
            attr_name, default_value
        )
