from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Type, get_type_hints


DEFAULT_CONTENT_TYPE = 'application/json'
ASYNCAPI_VERSION = '2.0.0'
ASYNCAPI_PYTHON_VERSION = '2.1.0'


@dataclass
class Specification:
    info: 'Info'
    channels: Dict[str, 'Channel']
    servers: Optional[Dict[str, 'Server']] = None
    components: Optional['Components'] = None
    tags: Optional[List['Tag']] = None
    external_docs: Optional['ExternalDocumentation'] = None
    default_content_type: str = DEFAULT_CONTENT_TYPE
    asyncapi: str = ASYNCAPI_VERSION


@dataclass(init=False)
class AutoSpec(Specification):
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
                url=uri, protocol=ProtocolType(protocol), name=server_name,
            )

    def subscribe(
        self,
        subscbriber_: Optional[Callable[..., Any]] = None,
        *,
        channel_name: str,
        channel_description: str = '',
        message_name: str = '',
        message_title: str = '',
        message_summary: str = '',
    ) -> Callable[..., Callable[..., Any]]:
        if not message_name:
            message_name = channel_name

        message_name = message_name.replace('/', '_')
        message_name = message_name.replace('#', '_')
        message_name = message_name.replace(' ', '_')
        message_name = as_camel_case(message_name)
        message_component_name = message_name[0].upper() + message_name[1:]

        def decorator(subscbriber: Callable[..., Any]) -> Callable[..., Any]:
            message_type = get_type_hints(subscbriber).get('message')
            message = Message(
                name=message_name,
                title=message_title,
                summary=message_summary,
                payload=message_type,
            )
            self.channels[channel_name] = subscbriber.__channel__ = Channel(  # type: ignore
                description=channel_description,
                subscribe=Operation(
                    operation_id=subscbriber.__name__, message=message,
                ),
                publish=Operation(message=message),
                name=channel_name,
            )
            if self.components and self.components.messages:
                self.components.messages[message_component_name] = message

            elif self.components:
                self.components.messages = {message_component_name: message}

            else:
                self.components = Components(
                    messages={message_component_name: message}
                )

            return subscbriber

        if subscbriber_:
            return decorator(subscbriber_)
        else:
            return decorator


@dataclass
class Contact:
    name: Optional[str] = None
    url: Optional[str] = None
    email: Optional[str] = None


@dataclass
class License:
    name: str
    url: Optional[str] = None


@dataclass
class Info:
    title: str
    version: str
    description: Optional[str] = None
    terms_of_service: Optional[str] = None
    contact: Optional[Contact] = None
    license: Optional[License] = None


class ProtocolType(Enum):
    KAFKA = 'kafka'
    REDIS = 'redis'
    POSTGRES = 'postgres'
    GCLOUD_PUBSUB = 'gcloud-pubsub'


@dataclass
class ServerVariable:
    enum: Optional[List[str]] = None
    default: Optional[str] = None
    description: Optional[str] = None
    examples: Optional[List[str]] = None


@dataclass
class Server:
    url: str
    protocol: ProtocolType
    protocol_version: Optional[str] = None
    description: Optional[str] = None
    variables: Optional[Dict[str, ServerVariable]] = None
    security: Optional[Dict[str, List[str]]] = None
    bindings: Optional[Dict[ProtocolType, Any]] = None
    name: Optional[str] = None


@dataclass
class CorrelationId:
    location: str
    description: Optional[str] = None


@dataclass
class ExternalDocumentation:
    url: str
    description: Optional[str] = None


@dataclass
class Tag:
    name: str
    description: Optional[str] = None
    external_docs: Optional[ExternalDocumentation] = None


@dataclass
class MessageTrait:
    headers: Optional[Dict[str, Any]] = None
    correlation_id: Optional[CorrelationId] = None
    schema_format: Optional[str] = None
    content_type: Optional[str] = None
    name: Optional[str] = None
    title: Optional[str] = None
    summary: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[Tag]] = None
    external_docs: Optional[ExternalDocumentation] = None
    bindings: Optional[Dict[ProtocolType, Any]] = None
    examples: Optional[List[Dict[str, Any]]] = None


@dataclass
class Message:
    headers: Optional[Dict[str, Any]] = None
    payload: Optional[Type[Any]] = None
    correlation_id: Optional[CorrelationId] = None
    schema_format: Optional[str] = None
    content_type: Optional[str] = None
    name: Optional[str] = None
    title: Optional[str] = None
    summary: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[Tag]] = None
    external_docs: Optional[ExternalDocumentation] = None
    bindings: Optional[Dict[ProtocolType, Any]] = None
    examples: Optional[List[Dict[str, Any]]] = None
    traits: Optional[List[MessageTrait]] = None


@dataclass
class OperationTrait:
    operation_id: Optional[str] = None
    summary: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[Tag]] = None
    external_docs: Optional[ExternalDocumentation] = None
    bindings: Optional[Dict[ProtocolType, Any]] = None


@dataclass
class Operation:
    operation_id: Optional[str] = None
    summary: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[Tag]] = None
    external_docs: Optional[ExternalDocumentation] = None
    bindings: Optional[Dict[ProtocolType, Any]] = None
    traits: Optional[List[OperationTrait]] = None
    message: Optional[Message] = None


@dataclass
class Parameter:
    description: Optional[str] = None
    schema: Optional[Type[Any]] = None
    location: Optional[str] = None


@dataclass
class Channel:
    description: Optional[str] = None
    publish: Optional[Operation] = None
    subscribe: Optional[Operation] = None
    parameters: Optional[Dict[str, Parameter]] = None
    bindings: Optional[Dict[ProtocolType, Any]] = None
    name: Optional[str] = None


@dataclass
class Components:
    messages: Optional[Dict[str, Message]] = None
    schemas: Optional[Dict[str, Any]] = None


def as_camel_case(snake_str: str) -> str:
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])
