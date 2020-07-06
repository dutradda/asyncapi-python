import asynctest
import pytest

import asyncapi.exceptions


@pytest.fixture
def fake_api():
    return asyncapi.build_api_auto_spec(
        server_url='kafka://fake.fake',
        channel='fake',
        operations_module='asyncapi._tests',
        operation_id='fake_operation',
    )


def test_should_get_api(fake_api):
    assert fake_api.spec
    assert fake_api.operations


@pytest.mark.asyncio
async def test_should_publish_message(
    fake_api, fake_broadcast, message, mocker, json_message
):
    await fake_api.publish('fake', message)

    assert fake_broadcast.publish.call_args_list == [
        mocker.call(channel='fake', message=json_message)
    ]


@pytest.mark.asyncio
async def test_should_listen_message(
    fake_api, fake_broadcast, message, mocker
):
    fake_operation = asynctest.CoroutineMock()
    fake_api.operations[('fake', 'fake_operation')] = fake_operation
    await fake_api.listen('fake')

    assert fake_broadcast.subscribe.call_args_list == [
        mocker.call(channel='fake')
    ]
    assert fake_operation.call_args_list == [mocker.call(message)]


@pytest.mark.asyncio
async def test_should_not_publish_for_invalid_channel(
    fake_api, message, mocker
):
    with pytest.raises(asyncapi.exceptions.InvalidChannelError) as exc_info:
        await fake_api.publish('faked', message)

    assert exc_info.value.args == ('faked',)


@pytest.mark.asyncio
async def test_should_not_listen_for_invalid_channel(
    fake_api, message, mocker
):
    with pytest.raises(asyncapi.exceptions.InvalidChannelError) as exc_info:
        await fake_api.listen('faked')

    assert exc_info.value.args == ('faked',)
