import pytest

import asyncapi.subscriber
from asyncapi import UrlOrModuleRequiredError


@pytest.fixture
def fake_loop(mocker, autouse=True):
    return mocker.patch.object(
        asyncapi.subscriber, 'get_event_loop'
    ).return_value


@pytest.fixture
def fake_environ(mocker, autouse=True):
    return mocker.patch.object(
        asyncapi.subscriber.os, 'environ', {'ASYNCAPI_WORKERS': 2}
    )


@pytest.fixture
def fake_fork(mocker, autouse=True):
    return mocker.patch.object(asyncapi.subscriber.os, 'fork')


@pytest.mark.asyncio
async def test_should_run_subscriber_for_spec(fake_loop):
    asyncapi.subscriber.main(
        url='fake_url',
        server='development',
        api_module='asyncapi._tests',
        channel=None,
    )
    await fake_loop.create_task.call_args_list[0][0][0]

    assert fake_loop.run_forever.called


@pytest.mark.asyncio
async def test_should_run_subscriber_for_auto_spec(fake_loop):
    asyncapi.subscriber.main(
        api_module='asyncapi._tests', channel='fake', url=None, server=None,
    )
    await fake_loop.create_task.call_args_list[0][0][0]

    assert fake_loop.run_forever.called


def test_should_raise_url_or_module_required_error():
    with pytest.raises(UrlOrModuleRequiredError):
        asyncapi.subscriber.main(
            url=None, channel='fake', server=None, api_module=None,
        )
