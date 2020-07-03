import pytest

import asyncapi.subscriber
from asyncapi import ChannelRequiredError, UrlRequiredError


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
        channel='fake',
        server='development',
        operations_module='asyncapi._tests',
        operation_id=None,
        server_url=None,
    )
    await fake_loop.create_task.call_args_list[0][0][0]

    assert fake_loop.run_forever.called


@pytest.mark.asyncio
async def test_should_run_subscriber_for_auto_spec(fake_loop):
    asyncapi.subscriber.main(
        channel='fake',
        operations_module='asyncapi._tests',
        operation_id='fake_operation',
        server_url='kafka://fake.fake',
    )
    await fake_loop.create_task.call_args_list[0][0][0]

    assert fake_loop.run_forever.called


def test_should_raise_channel_required_error():
    with pytest.raises(ChannelRequiredError):
        asyncapi.subscriber.main(channel=None,)


def test_should_raise_url_required_error():
    with pytest.raises(UrlRequiredError):
        asyncapi.subscriber.main(
            url=None, channel='fake', server_url=None,
        )
