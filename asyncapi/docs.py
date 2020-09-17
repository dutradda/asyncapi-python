import dataclasses
import importlib
import json
from enum import Enum
from http import HTTPStatus
from typing import Any, Dict, Iterable, List

import typer
import uvicorn
import yaml
from apidaora import (
    ContentType,
    Response,
    RoutedControllerTypeHint,
    appdaora,
    route,
)

from asyncapi import AutoSpec
from asyncapi.schema import type_as_jsonschema


def main(
    api_module: str = typer.Option('', envvar='ASYNCAPI_MODULE'),
    host: str = typer.Option('0.0.0.0', envvar='ASYNCAPI_HOST'),
    port: int = typer.Option(5000, envvar='ASYNCAPI_PORT'),
) -> None:
    spec = getattr(importlib.import_module(api_module), 'spec')
    start(spec, host, port)


def start(spec: AutoSpec, host: str, port: int) -> None:
    app = appdaora(
        build_yaml_spec_controllers(spec) + [build_json_spec_controller(spec)]
    )
    uvicorn.run(app, host=host, port=port)


def build_yaml_spec_controllers(
    spec: AutoSpec,
) -> List[RoutedControllerTypeHint]:
    def controller() -> Response:
        return Response(
            status=HTTPStatus.OK,
            content_type=ContentType.APPLICATION_YAML,
            body=yaml.dump(spec_asjson(spec)),
            headers=(),
        )

    @route.get('/asyncapi.yaml')
    def controller_yaml() -> Response:
        return controller()

    @route.get('/asyncapi.yml')
    def controller_yml() -> Response:
        return controller()

    return [controller_yaml, controller_yml]


def build_json_spec_controller(spec: AutoSpec) -> RoutedControllerTypeHint:
    @route.get('/asyncapi.json')
    def controller() -> Response:
        return Response(
            status=HTTPStatus.OK,
            content_type=ContentType.APPLICATION_JSON,
            body=json.dumps(spec_asjson(spec), indent=2).encode(),
            headers=(),
        )

    return controller


def spec_asjson(spec: AutoSpec) -> Dict[str, Any]:
    json_spec: Dict[str, Any] = _spec_asjson(spec)

    for server in json_spec['servers'].values():
        server.pop('name', None)

    for channel_dict, channel in zip(
        json_spec['channels'].values(), spec.channels.values()
    ):
        channel_dict.pop('name')
        channel_dict['subscribe']['message'].pop('contentType', None)

        if (
            channel.subscribe
            and channel.subscribe.message
            and channel.subscribe.message.payload
        ):
            channel_dict['subscribe']['message'][
                'payload'
            ] = type_as_jsonschema(channel.subscribe.message.payload)

    return json_spec


def _spec_asjson(generic_value: Any) -> Any:
    json_value: Any

    if dataclasses.is_dataclass(generic_value):
        json_value = {}

        for field in dataclasses.fields(generic_value):
            field_value = _spec_asjson(
                getattr(generic_value, field.name, None)
            )

            if field_value is not None and field_value != '':
                json_value[as_camel_case(field.name)] = field_value

    elif isinstance(generic_value, dict):
        json_value = {k: _spec_asjson(v) for k, v in generic_value.items()}

    elif not isinstance(generic_value, str) and isinstance(
        generic_value, Iterable
    ):
        json_value = [_spec_asjson(v) for v in generic_value]

    elif isinstance(generic_value, Enum):
        json_value = generic_value.value

    else:
        json_value = generic_value

    return json_value


def as_camel_case(snake_str: str) -> str:
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


def run() -> None:
    typer.run(main)


if __name__ == '__main__':
    run()
