import pytest

import asyncapi.subscriber
from asyncapi import UrlOrModuleRequiredError


@pytest.fixture
def fake_loop(mocker):
    return mocker.patch.object(
        asyncapi.subscriber, 'get_event_loop'
    ).return_value


@pytest.fixture(autouse=True)
def fake_fork(mocker):
    mock = mocker.patch.object(asyncapi.subscriber.os, 'fork')
    mock.return_value = 0
    return mock


@pytest.mark.asyncio
async def test_should_run_subscriber_for_spec(fake_loop):
    asyncapi.subscriber.main(
        url='fake_url',
        server='development',
        api_module='asyncapi._tests',
        channel=None,
        server_bindings=None,
        channels_subscribes=None,
        workers=2,
    )
    await fake_loop.create_task.call_args_list[0][0][0]

    assert fake_loop.run_forever.called


@pytest.mark.asyncio
async def test_should_run_subscriber_for_auto_spec(fake_loop):
    asyncapi.subscriber.main(
        api_module='asyncapi._tests',
        channel='fake',
        server_bindings=None,
        url=None,
        server=None,
        workers=2,
        channels_subscribes=None,
    )
    await fake_loop.create_task.call_args_list[0][0][0]

    assert fake_loop.run_forever.called


def test_should_raise_url_or_module_required_error():
    with pytest.raises(UrlOrModuleRequiredError):
        asyncapi.subscriber.main(
            url=None,
            channel='fake',
            server_bindings=None,
            server=None,
            api_module=None,
            workers=2,
            channels_subscribes=None,
        )
