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
from .entities import (
    Channel,
    Components,
    Info,
    Message,
    ProtocolType,
    Server,
    Specification,
    Subscribe,
)
from .exceptions import ReferenceNotFoundError


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
    operations = build_channel_operations(spec, module_name)

    if server is None:
        server = tuple(spec.servers.keys())[-1]

    protocol = spec.servers[server].protocol.value
    url = spec.servers[server].url
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
            if channel.subscribe.operation_id
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

    return Specification(
        info=Info(**spec['info']),
        servers={
            server_name: Server(
                name=server_name,
                protocol=ProtocolType(server_spec.pop('protocol')),
                **server_spec,
            )
            for server_name, server_spec in spec['servers'].items()
        },
        channels={
            channel_name: Channel(
                name=channel_name,
                subscribe=Subscribe(
                    message=Message(
                        content_type=channel_spec['subscribe']['message'].get(
                            'contentType', spec.get('defaultContentType')
                        ),
                        payload=jsonschema_asdataclass(
                            channel_spec['subscribe']['message'][
                                'name'
                            ].replace(' ', ''),
                            channel_spec['subscribe']['message'].get(
                                'payload'
                            ),
                        ),
                        **{
                            k: v
                            for k, v in channel_spec['subscribe'][
                                'message'
                            ].items()
                            if k != 'contentType' and k != 'payload'
                        },
                    ),
                    operation_id=channel_spec.pop('subscribe').get(
                        'operationId', None
                    ),
                ),
                **channel_spec,
            )
            for channel_name, channel_spec in spec['channels'].items()
        },
        components=Components(
            messages={
                msg_id: Message(
                    content_type=message.get(
                        'contentType', spec.get('defaultContentType')
                    ),
                    payload=jsonschema_asdataclass(
                        message['name'].replace(' ', ''),
                        message.get('payload'),
                    ),
                    **{
                        k: v
                        for k, v in message.items()
                        if k != 'contentType' and k != 'payload'
                    },
                )
                for msg_id, message in spec['components']['messages'].items()
            }
            if 'messages' in spec['components']
            else None,
            schemas=spec['components'].get('schemas'),
        )
        if 'components' in spec
        else None,
        default_content_type=spec.get('defaultContentType'),
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
