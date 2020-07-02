import dataclasses
from enum import Enum
from typing import Any, Dict, Optional


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
    servers: Dict[str, Server]
    channels: Dict[str, Channel]
    components: Optional[Components] = None
    default_content_type: Optional[str] = None
