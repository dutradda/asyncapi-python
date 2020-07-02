"""
Doodle
"""

__version__ = '0.1.0'


import importlib
from collections import deque
from typing import Any, Dict, Optional

import yaml

from .entities import (
    AsyncApi,
    Channel,
    Components,
    Info,
    Message,
    OperationsTypeHint,
    ProtocolType,
    Server,
    Specification,
    Subscribe,
)
from .exceptions import ReferenceNotFoundError


def api(path: str) -> AsyncApi:
    spec = build_spec(load_spec_dict(path))
    operations = build_channel_operations(spec)
    return AsyncApi(spec, operations)


def build_channel_operations(spec: Specification) -> OperationsTypeHint:
    operations: OperationsTypeHint = {}

    for channel in spec.channels:
        if channel.subscribe.operation_id:
            mod_parts = channel.subscribe.operation_id.split('.')
            op_name = mod_parts[-1]
            mod_name = '.'.join(mod_parts[:-1])
            operations[op_name] = getattr(
                importlib.import_module(mod_name), op_name
            )

    return operations


def load_spec_dict(path: str) -> Dict[str, Any]:
    spec: Dict[str, Any] = yaml.safe_load(open(path))
    return spec


def build_spec(spec: Dict[str, Any]) -> Specification:
    fill_refs(spec)

    return Specification(
        info=Info(**spec['info']),
        servers=[
            Server(
                name=server_name,
                protocol=ProtocolType(server_spec.pop('protocol')),
                **server_spec,
            )
            for server_name, server_spec in spec['servers'].items()
        ],
        channels=[
            Channel(
                name=channel_name,
                subscribe=Subscribe(
                    message=Message(**channel_spec['subscribe']['message']),
                    operation_id=channel_spec.pop('subscribe').get(
                        'operationId', None
                    ),
                ),
                **channel_spec,
            )
            for channel_name, channel_spec in spec['channels'].items()
        ],
        components=Components(
            messages={
                msg_id: Message(**message)
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
