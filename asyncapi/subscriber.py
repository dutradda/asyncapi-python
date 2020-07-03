import os
import signal
import time
from asyncio import AbstractEventLoop, get_event_loop
from typing import Any, Optional

import typer

from asyncapi import (
    AsyncApi,
    ChannelRequiredError,
    UrlRequiredError,
    build_api,
    build_api_auto_spec,
)


def main(
    url: Optional[str] = typer.Option(None, envvar='ASYNCAPI_URL'),
    channel: Optional[str] = typer.Option(None, envvar='ASYNCAPI_CHANNEL'),
    server: str = typer.Option('development', envvar='ASYNCAPI_SERVER'),
    operations_module: str = typer.Option(
        '', envvar='ASYNCAPI_OPERATIONS_MODULE'
    ),
    operation_id: Optional[str] = typer.Option(
        None, envvar='ASYNCAPI_OPERATION_ID'
    ),
    server_url: Optional[str] = typer.Option(
        None, envvar='ASYNCAPI_SERVER_URL'
    ),
    republish_errors: bool = typer.Option(
        True, envvar='ASYNCAPI_REPUBLISH_ERRORS'
    ),
) -> None:
    fork_server()

    if channel is None:
        raise ChannelRequiredError()

    if server_url and operation_id and operations_module:
        api = build_api_auto_spec(
            server_url,
            channel,
            operations_module,
            operation_id,
            republish_errors=republish_errors,
        )

    elif url is None:
        raise UrlRequiredError()

    else:
        api = build_api(
            url,
            server=server,
            operations_module=operations_module,
            republish_errors=republish_errors,
        )

    graceful_stop()
    loop = get_event_loop()
    start(loop, api, channel)
    loop.run_forever()


def start(loop: AbstractEventLoop, api: AsyncApi, channel: str) -> None:
    async def init() -> None:
        await api.broadcast.connect()
        await api.listen(channel)

    task = loop.create_task(init())
    task.add_done_callback(task_callback)

    typer.echo('Waiting messages...')


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


def task_callback(future: Any) -> None:
    future.result()  # pragma: no cover


def run() -> None:
    typer.run(main)  # pragma: no cover


def fork_server() -> None:
    workers = int(os.environ.get('ASYNCAPI_WORKERS', 1))

    if workers > 1:
        typer.echo(f'Forking for {workers} workers')
        for _ in range(workers - 1):
            pid = os.fork()
            if pid == 0:
                break
