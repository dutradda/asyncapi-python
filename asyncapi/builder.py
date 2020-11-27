"""
asyncapi
"""
import importlib
import io
from collections import defaultdict, deque
from typing import Any, DefaultDict, Dict, List, Optional

import requests
import yaml
from jsondaora import jsonschema_asdataclass

from .api import AsyncApi, OperationsTypeHint
from .events.handler import EventsHandler
from .exceptions import (
    EmptyServersError,
    InvalidAsyncApiVersionError,
    InvalidChannelsSubscribersError,
    InvalidContentTypeError,
    InvalidServerBindingError,
    InvalidServerBindingProtocolError,
    ReferenceNotFoundError,
    ServerNotFoundError,
)
from .specification_v2_0_0 import (
    ASYNCAPI_PYTHON_VERSION,
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
    Tag,
)


def build_api(
    path: str,
    server: Optional[str] = None,
    module_name: str = '',
    republish_errors: Optional[bool] = None,
    server_bindings: Optional[str] = None,
    channels_subscribes: Optional[str] = None,
    republish_errors_channels: Optional[str] = None,
) -> AsyncApi:
    spec = build_spec_from_path(path)
    set_api_spec_server_bindings(spec, server_bindings)
    set_api_spec_channels_subscribes(spec, channels_subscribes)
    return build_api_from_spec(
        spec, module_name, server, republish_errors, republish_errors_channels
    )


def build_api_auto_spec(
    module_name: str,
    server: Optional[str] = None,
    republish_errors: Optional[bool] = None,
    server_bindings: Optional[str] = None,
    channels_subscribes: Optional[str] = None,
    republish_errors_channels: Optional[str] = None,
) -> AsyncApi:
    spec = getattr(importlib.import_module(module_name), 'spec')
    set_api_spec_server_bindings(spec, server_bindings)
    set_api_spec_channels_subscribes(spec, channels_subscribes)
    return build_api_from_spec(
        spec, module_name, server, republish_errors, republish_errors_channels
    )


def build_spec_from_path(path: str) -> Specification:
    return build_spec(load_spec_dict(path))


def set_api_spec_server_bindings(
    spec: Specification, server_bindings: Optional[str]
) -> None:
    if server_bindings and spec.servers:
        binding_str_list = server_bindings.split(',')
        bindings_spec: DefaultDict[str, Dict[str, str]] = defaultdict(dict)

        for binding_str in binding_str_list:
            try:
                protocol_str, protocol_bind_str = binding_str.split(':')
            except ValueError:
                raise InvalidServerBindingError(binding_str)

            try:
                protocol_bind_list = protocol_bind_str.split(';')
            except ValueError:
                raise InvalidServerBindingError(binding_str)

            for protocol_bind_str in protocol_bind_list:
                try:
                    binding_name, binding_value = protocol_bind_str.split('=')
                except ValueError:
                    raise InvalidServerBindingError(protocol_bind_str)

                bindings_spec[protocol_str][binding_name] = binding_value

        for server_name, server in spec.servers.items():
            new_server_bindings = build_server_bindings(
                server_name, server.protocol, bindings_spec
            )

            if new_server_bindings:
                for protocol, binding in new_server_bindings.items():
                    already_server_bindings = server.bindings

                    if already_server_bindings:
                        if protocol in already_server_bindings:
                            already_server_bindings[protocol].update(binding)
                        else:
                            already_server_bindings[protocol] = binding

                    else:
                        server.bindings = {protocol: binding}


def set_api_spec_channels_subscribes(
    spec: Specification, channels_subscribes: Optional[str]
) -> None:
    if channels_subscribes:
        channels_subscribes_list = channels_subscribes.split(',')
        channels_subscribes_dict = {}
        new_channels = {}

        for channels_subscribes_str in channels_subscribes_list:
            try:
                (
                    publish_channel,
                    subscribe_operation_id,
                ) = channels_subscribes_str.split(':')
            except ValueError:
                InvalidChannelsSubscribersError(channels_subscribes_str)

            if '=' in subscribe_operation_id:
                try:
                    (
                        subscribe_channel,
                        subscribe_operation_id,
                    ) = subscribe_operation_id.split('=')
                except ValueError:
                    InvalidChannelsSubscribersError(channels_subscribes_str)
            else:
                subscribe_channel = publish_channel

            channels_subscribes_dict[publish_channel] = (
                subscribe_channel,
                subscribe_operation_id,
            )

        for channel_name, channel in spec.channels.items():
            if (
                channel.subscribe is None
                and channel.publish
                and channel_name in channels_subscribes_dict
            ):
                (
                    subscribe_channel_name,
                    operation_id,
                ) = channels_subscribes_dict[channel_name]
                subscribe = Operation(
                    operation_id=operation_id,
                    summary=channel.publish.summary,
                    description=channel.publish.description,
                    tags=channel.publish.tags,
                    external_docs=channel.publish.external_docs,
                    bindings=channel.publish.bindings,
                    traits=channel.publish.traits,
                    message=channel.publish.message,
                )

                if subscribe_channel_name == channel_name:
                    channel.subscribe = subscribe
                else:
                    new_channels[subscribe_channel_name] = Channel(
                        description=channel.description,
                        subscribe=subscribe,
                        parameters=channel.parameters,
                        bindings=channel.bindings,
                        name=subscribe_channel_name,
                    )

        spec.channels.update(new_channels)


def build_api_from_spec(
    spec: Specification,
    module_name: str,
    server_name: Optional[str],
    republish_errors: Optional[bool],
    republish_errors_channels: Optional[str],
) -> AsyncApi:
    if spec.servers is None or not spec.servers:
        raise EmptyServersError()

    if server_name is None:
        server_name = tuple(spec.servers.keys())[-1]

    try:
        server = spec.servers[server_name]
    except KeyError:
        ServerNotFoundError(server_name)

    if module_name:
        try:
            logger = getattr(importlib.import_module(module_name), 'logger')
        except (ImportError, AttributeError):
            logger = AsyncApi.logger
    else:
        logger = AsyncApi.logger

    operations = build_channel_operations(spec, module_name)
    events_handler = EventsHandler(
        url=f'{server.protocol.value}://{server.url}',
        bindings=server.bindings.get(server.protocol, {})
        if server.bindings
        else {},
    )

    republish_errors_channels_dict: Optional[Dict[str, str]]
    if republish_errors_channels is not None:
        republish_errors_channels_dict = {
            channel_str.split('=')[0]: channel_str.split('=')[1]
            for channel_str in republish_errors_channels.split(';')
        }
    else:
        republish_errors_channels_dict = None

    if republish_errors is not None:
        kwargs = dict(republish_error_messages=republish_errors)
    else:
        kwargs = {}

    return AsyncApi(
        spec,
        operations,
        events_handler,
        republish_error_messages_channels=republish_errors_channels_dict,
        logger=logger,
        **kwargs,
    )


def build_channel_operations(
    spec: Specification, module_name: str
) -> OperationsTypeHint:
    operations = {}

    if module_name:
        for channel_name, channel in spec.channels.items():
            if channel.subscribe and channel.subscribe.operation_id:
                operation = getattr(
                    importlib.import_module(module_name),
                    channel.subscribe.operation_id,
                    None,
                )

                if operation:
                    operation_key = (
                        channel_name,
                        channel.subscribe.operation_id,
                    )
                    operations[operation_key] = operation

    return operations


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
            server_name: build_server(server_name, server_spec)
            for server_name, server_spec in spec['servers'].items()
        }
        if 'servers' in spec
        else None,
        channels=build_channels(spec),
        components=build_components(spec.get('components')),
        tags=build_tags(spec.get('tags')),
    )


def build_server(server_name: str, server_spec: Dict[str, Any]) -> Server:
    protocol = ProtocolType(server_spec.pop('protocol'))
    bindings = build_server_bindings(
        server_name, protocol, server_spec.pop('bindings', None)
    )
    return Server(
        name=server_name, protocol=protocol, bindings=bindings, **server_spec,
    )


def build_server_bindings(
    server_name: str,
    server_protocol: ProtocolType,
    bindings_spec: Optional[Dict[str, Dict[str, str]]],
) -> Optional[Dict[ProtocolType, Dict[str, str]]]:
    if bindings_spec:
        server_bindings = {}

        for protocol_str, bindings in bindings_spec.items():
            try:
                binding_protocol = ProtocolType(protocol_str)
            except ValueError:
                raise InvalidServerBindingProtocolError(
                    server_name, protocol_str
                )

            if binding_protocol != server_protocol:
                raise InvalidServerBindingProtocolError(
                    server_name, protocol_str
                )

            server_bindings[binding_protocol] = bindings

        return server_bindings

    return None


def validate_content_type(content_type: str) -> None:
    if content_type != DEFAULT_CONTENT_TYPE:
        raise InvalidContentTypeError(
            content_type, f'valid content types: {DEFAULT_CONTENT_TYPE}'
        )


def validate_asyncapi_version(asyncapi_version: str) -> None:
    if asyncapi_version not in (ASYNCAPI_VERSION, ASYNCAPI_PYTHON_VERSION):
        raise InvalidAsyncApiVersionError(
            asyncapi_version,
            (
                f'valid versions: {ASYNCAPI_VERSION}, '
                f'{ASYNCAPI_PYTHON_VERSION}',
            ),
        )


def build_channels(spec: Dict[str, Any]) -> Dict[str, Channel]:
    channels = {}
    messages = spec.get('components', {}).get('messages', {})

    for channel_name, channel_spec in spec['channels'].items():
        channels[channel_name] = Channel(
            name=channel_name,
            subscribe=build_operation(
                channel_spec.pop('subscribe', None), messages
            ),
            publish=build_operation(
                channel_spec.pop('publish', None), messages
            ),
            **channel_spec,
        )

    return channels


def build_operation(
    operation_spec: Optional[Dict[str, Any]], messages: Dict[str, Any],
) -> Optional[Operation]:
    if operation_spec is None:
        return None

    message_spec = operation_spec.get('message')

    if 'name' not in message_spec:  # type: ignore
        for message_name, message_payload in messages.items():
            if message_payload == message_spec:
                message_spec['name'] = message_name
                break

    return Operation(
        message=build_message(message_spec) if message_spec else None,
        operation_id=operation_spec.get('operationId'),
        tags=build_tags(operation_spec.get('tags')),
    )


def build_message(message_spec: Dict[str, Any]) -> Message:
    content_type = message_spec.get('contentType')

    if content_type:
        validate_content_type(content_type)

    return Message(
        content_type=content_type,
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


def build_tags(
    tags_spec: Optional[List[Dict[str, Any]]]
) -> Optional[List[Tag]]:
    if tags_spec:
        return [Tag(**tag_spec) for tag_spec in tags_spec]

    return None


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
