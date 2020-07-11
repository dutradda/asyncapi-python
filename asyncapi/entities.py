import dataclasses
from enum import Enum
from typing import Any, Callable, Dict, Optional, Type, get_type_hints


@dataclasses.dataclass
class Info:
    title: str
    version: str
    description: str


class ProtocolType(Enum):
    KAFKA = 'kafka'
    REDIS = 'redis'
    POSTGRES = 'postgres'
    GCLOUD_PUBSUB = 'gcloud-pubsub'


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
    payload: Optional[Type[Any]]


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


@dataclasses.dataclass(init=False)
class Spec(Specification):
    def __init__(
        self,
        title: str,
        description: str = '',
        version: str = '1.0.0',
        **servers: str,
    ) -> None:
        self.info = Info(title, version, description)
        self.servers = {}
        self.channels = {}

        for server_name, url in servers.items():
            protocol, uri = url.split('://')
            self.servers[server_name] = Server(
                server_name, uri, ProtocolType(protocol), description=''
            )

    def subscribe(
        self,
        *,
        channel_name: str,
        channel_description: str = '',
        message_name: str = '',
        message_title: str = '',
        message_summary: str = '',
    ) -> Callable[..., Callable[..., Any]]:
        def decorator(subscbriber: Callable[..., Any]) -> Callable[..., Any]:
            message_type = get_type_hints(subscbriber).get('message')
            message = Message(
                name=message_name or channel_name,
                title=message_title,
                summary=message_summary,
                content_type='application/json',
                payload=message_type,
            )
            self.channels[channel_name] = subscbriber.__channel__ = Channel(  # type: ignore
                channel_name,
                channel_description,
                Subscribe(message, subscbriber.__name__),
            )
            return subscbriber

        return decorator
