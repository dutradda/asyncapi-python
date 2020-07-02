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


def api(
    path: str, server: str = 'production', operations_module: str = ''
) -> AsyncApi:
    spec = build_spec(load_spec_dict(path))
    operations = build_channel_operations(spec, operations_module)
    protocol = spec.servers[server].protocol.value
    url = spec.servers[server].url
    broadcast = Broadcast(f'{protocol}://{url}')
    return AsyncApi(spec, operations, broadcast)


def build_channel_operations(
    spec: Specification, operations_module: str
) -> OperationsTypeHint:
    if operations_module:
        return {
            (channel_name, channel.subscribe.operation_id): getattr(
                importlib.import_module(operations_module),
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
                        **{
                            k: v
                            for k, v in channel_spec['subscribe'][
                                'message'
                            ].items()
                            if k != 'contentType'
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
                    **{k: v for k, v in message.items() if k != 'contentType'},
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
