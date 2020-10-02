import os
import signal
import time
from asyncio import AbstractEventLoop, get_event_loop
from typing import Any, Optional

import typer

from asyncapi import (
    AsyncApi,
    UrlOrModuleRequiredError,
    build_api,
    build_api_auto_spec,
)


def main(
    url: Optional[str] = typer.Option(None, envvar='ASYNCAPI_URL'),
    server: Optional[str] = typer.Option(None, envvar='ASYNCAPI_SERVER'),
    server_bindings: Optional[str] = typer.Option(
        None, envvar='ASYNCAPI_SERVER_BINDINGS'
    ),
    api_module: str = typer.Option('', envvar='ASYNCAPI_MODULE'),
    republish_errors: Optional[bool] = typer.Option(
        None, envvar='ASYNCAPI_REPUBLISH_ERRORS'
    ),
    channel: Optional[str] = typer.Option(None, envvar='ASYNCAPI_CHANNEL'),
    workers: int = typer.Option(1, envvar='ASYNCAPI_WORKERS'),
    channels_subscribes: Optional[str] = typer.Option(
        None, envvar='ASYNCAPI_CHANNELS_SUBSCRIBES'
    ),
    republish_errors_channels: Optional[str] = typer.Option(
        None, envvar='ASYNCAPI_REPUBLISH_ERRORS_CHANNELS'
    ),
) -> None:

    if url is None:
        if api_module is None:
            raise UrlOrModuleRequiredError()

        api = build_api_auto_spec(
            module_name=api_module,
            server=server,
            server_bindings=server_bindings,
            republish_errors=republish_errors,
            channels_subscribes=channels_subscribes,
            republish_errors_channels=republish_errors_channels,
        )

    else:
        api = build_api(
            url,
            server=server,
            module_name=api_module,
            server_bindings=server_bindings,
            republish_errors=republish_errors,
            channels_subscribes=channels_subscribes,
            republish_errors_channels=republish_errors_channels,
        )

    fork_app(workers)
    graceful_stop()
    loop = get_event_loop()
    start(loop, api, channel)
    loop.run_forever()


def start(
    loop: AbstractEventLoop, api: AsyncApi, channel: Optional[str]
) -> None:
    async def init() -> None:
        async with api as api_:
            if channel is None:
                await api_.listen_all()
            else:
                await api_.listen(channel)

    task = loop.create_task(init())
    task.add_done_callback(task_callback)

    typer.echo('Waiting messages...')


def task_callback(future: Any) -> None:
    future.result()  # pragma: no cover


def run() -> None:
    typer.run(main)


def graceful_stop() -> None:
    def exit_gracefully(signum: int = -1, frame: Any = None) -> None:
        signame = {  # type: ignore
            signal.SIGINT: 'SIGINT',
            signal.SIGTERM: 'SIGTERM',
        }.get(signum)
        typer.echo(f'Received {signame} scheduling shutdown...')

        time.sleep(1)
        raise SystemExit(0)

    signal.signal(signal.SIGINT, exit_gracefully)
    signal.signal(signal.SIGTERM, exit_gracefully)


def fork_app(workers: int) -> None:
    if workers > 1:
        typer.echo(f'Forking for {workers} workers')
        for _ in range(workers - 1):
            pid = os.fork()
            if pid == 0:
                break


if __name__ == '__main__':
    run()
