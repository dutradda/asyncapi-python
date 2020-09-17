"""
asyncapi
"""

__version__ = '0.2.0'
import importlib
import io
from collections import deque
from typing import Any, Dict, Optional

import requests
import yaml
from broadcaster import Broadcast
from jsondaora import jsonschema_asdataclass

from .api import AsyncApi, OperationsTypeHint
from .exceptions import (
    EmptyServersError,
    InvalidAsyncApiVersionError,
    InvalidContentTypeError,
    ReferenceNotFoundError,
    ServerNotFoundError,
)
from .specification_v2_0_0 import (
    ASYNCAPI_VERSION,
    DEFAULT_CONTENT_TYPE,
    Channel,
    Components,
    Info,
    Message,
    Operation,
    ProtocolType,
    Server,
    Specification,
)


def build_api(
    path: str,
    server: Optional[str] = None,
    module_name: str = '',
    republish_errors: bool = True,
) -> AsyncApi:
    spec = build_spec(load_spec_dict(path))
    return build_api_from_spec(spec, module_name, server, republish_errors)


def build_api_auto_spec(
    module_name: str,
    server: Optional[str] = None,
    republish_errors: bool = True,
) -> AsyncApi:
    spec = getattr(importlib.import_module(module_name), 'spec')
    return build_api_from_spec(spec, module_name, server, republish_errors)


def build_api_from_spec(
    spec: Specification,
    module_name: str,
    server: Optional[str],
    republish_errors: bool,
) -> AsyncApi:
    if spec.servers is None or not spec.servers:
        raise EmptyServersError()

    if server is None:
        server = tuple(spec.servers.keys())[-1]

    try:
        protocol = spec.servers[server].protocol.value
    except KeyError:
        ServerNotFoundError(server)

    url = spec.servers[server].url
    operations = build_channel_operations(spec, module_name)
    broadcast = Broadcast(f'{protocol}://{url}')

    return AsyncApi(
        spec, operations, broadcast, republish_error_messages=republish_errors
    )


def build_channel_operations(
    spec: Specification, module_name: str
) -> OperationsTypeHint:
    if module_name:
        return {
            (channel_name, channel.subscribe.operation_id): getattr(
                importlib.import_module(module_name),
                channel.subscribe.operation_id,
            )
            for channel_name, channel in spec.channels.items()
            if channel.subscribe and channel.subscribe.operation_id
        }

    return {}


def load_spec_dict(path: str) -> Dict[str, Any]:
    spec: Dict[str, Any]

    if path.startswith('http'):
        request = requests.get(path)
        request.raise_for_status()

        if path.endswith('.json'):
            spec = request.json()
        else:
            spec = yaml.safe_load(io.BytesIO(request.content))

    else:
        spec = yaml.safe_load(open(path))

    return spec


def build_spec(spec: Dict[str, Any]) -> Specification:
    fill_refs(spec)
    validate_content_type(spec.get('defaultContentType', DEFAULT_CONTENT_TYPE))
    validate_asyncapi_version(spec.get('asyncapi', ASYNCAPI_VERSION))

    return Specification(
        info=Info(**spec['info']),
        servers={
            server_name: Server(
                name=server_name,
                protocol=ProtocolType(server_spec.pop('protocol')),
                **server_spec,
            )
            for server_name, server_spec in spec['servers'].items()
        }
        if 'servers' in spec
        else None,
        channels=build_channels(spec),
        components=build_components(spec.get('components')),
    )


def validate_content_type(content_type: str) -> None:
    if content_type != DEFAULT_CONTENT_TYPE:
        raise InvalidContentTypeError(
            content_type, f'valid content types: {DEFAULT_CONTENT_TYPE}'
        )


def validate_asyncapi_version(asyncapi_version: str) -> None:
    if asyncapi_version != ASYNCAPI_VERSION:
        raise InvalidAsyncApiVersionError(
            asyncapi_version, f'valid versions: {ASYNCAPI_VERSION}'
        )


def build_channels(spec: Dict[str, Any]) -> Dict[str, Channel]:
    channels = {}

    for channel_name, channel_spec in spec['channels'].items():
        content_type = channel_spec['subscribe']['message'].get('contentType')

        if content_type:
            validate_content_type(content_type)

        channels[channel_name] = Channel(
            name=channel_name,
            subscribe=build_operation(channel_spec.pop('subscribe', None)),
            publish=build_operation(channel_spec.pop('publish', None)),
            **channel_spec,
        )

    return channels


def build_operation(
    operation_spec: Optional[Dict[str, Any]]
) -> Optional[Operation]:
    if operation_spec is None:
        return None

    message_spec = operation_spec.get('message')

    return Operation(
        message=build_message(message_spec) if message_spec else None,
        operation_id=operation_spec.get('operationId', None),
    )


def build_message(message_spec: Dict[str, Any]) -> Message:
    if message_spec is None:
        return None

    return Message(
        content_type=message_spec.get('contentType'),
        payload=jsonschema_asdataclass(
            message_spec['name'].replace(' ', ''),
            message_spec.get('payload', {}),
        ),
        **{
            k: v
            for k, v in message_spec.items()
            if k != 'contentType' and k != 'payload'
        },
    )


def build_components(
    components_spec: Optional[Dict[str, Any]]
) -> Optional[Components]:
    if components_spec is None:
        return None

    return Components(
        messages={
            msg_id: build_message(message_spec)
            for msg_id, message_spec in components_spec['messages'].items()
        }
        if 'messages' in components_spec
        else None,
        schemas=components_spec.get('schemas'),
    )


def fill_refs(
    spec: Dict[str, Any], full_spec: Optional[Dict[str, Any]] = None
) -> None:
    if full_spec is None:
        full_spec = spec

    for key, value in spec.items():
        if isinstance(value, dict):
            while '$ref' in value:
                spec[key] = value = dict_from_ref(spec[key]['$ref'], full_spec)

            fill_refs(value, full_spec)


def dict_from_ref(ref: str, spec: Dict[str, Any]) -> Dict[str, Any]:
    ref_keys = deque(ref.strip('#/').split('/'))

    while ref_keys and isinstance(spec, dict):
        spec = spec.get(ref_keys.popleft(), {})

    if not spec:
        raise ReferenceNotFoundError(ref)

    return spec
