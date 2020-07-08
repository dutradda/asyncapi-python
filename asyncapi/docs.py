import importlib
import json
from http import HTTPStatus
from typing import Any, Dict

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
from jsondaora import dataclasses

from asyncapi import Spec
from asyncapi.schema import type_as_jsonschema


def main(
    api_module: str = typer.Option('', envvar='ASYNCAPI_MODULE'),
    host: str = typer.Option('0.0.0.0', envvar='ASYNCAPI_HOST'),
    port: int = typer.Option(5000, envvar='ASYNCAPI_PORT'),
) -> None:
    spec = getattr(importlib.import_module(api_module), 'spec')
    start(spec, host, port)


def start(spec: Spec, host: str, port: int) -> None:
    app = appdaora(
        [build_yaml_spec_controller(spec), build_json_spec_controller(spec)]
    )
    uvicorn.run(app, host=host, port=port)


def build_yaml_spec_controller(spec: Spec) -> RoutedControllerTypeHint:
    @route.get('/asyncapi.yaml')
    def controller() -> Response:
        return Response(
            status=HTTPStatus.OK,
            content_type=ContentType.APPLICATION_YAML,
            body=yaml.dump(spec_asdict(spec)),
            headers=(),
        )

    return controller


def build_json_spec_controller(spec: Spec) -> RoutedControllerTypeHint:
    @route.get('/asyncapi.json')
    def controller() -> Response:
        dict_spec = spec_asdict(spec)
        return Response(
            status=HTTPStatus.OK,
            content_type=ContentType.APPLICATION_JSON,
            body=json.dumps(dict_spec, indent=2).encode(),
            headers=(),
        )

    return controller


def spec_asdict(spec: Spec) -> Dict[str, Any]:
    dict_spec: Dict[str, Any] = dataclasses.asdict(spec)
    dict_spec.pop('default_content_type')
    dict_spec['defaultContentType'] = 'application/json'

    for server in dict_spec['servers'].values():
        server.pop('name')

    if dict_spec['components'] is None:
        dict_spec.pop('components')

    for channel_dict, channel in zip(
        dict_spec['channels'].values(), spec.channels.values()
    ):
        channel_dict.pop('name')
        channel_dict['subscribe']['message'].pop('content_type')

        if 'operation_id' in channel_dict['subscribe']:
            channel_dict['subscribe']['operationId'] = channel_dict[
                'subscribe'
            ].pop('operation_id')

        if channel.subscribe.message.payload:
            channel_dict['subscribe']['message'][
                'payload'
            ] = type_as_jsonschema(channel.subscribe.message.payload)

    return dict_spec


def run() -> None:
    typer.run(main)


if __name__ == '__main__':
    run()
