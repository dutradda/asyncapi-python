import asynctest
import pytest

import asyncapi.exceptions


@pytest.fixture
def fake_api():
    return asyncapi.build_api_auto_spec('asyncapi._tests')


def test_should_get_api(fake_api):
    assert fake_api.spec
    assert fake_api.operations


@pytest.mark.asyncio
async def test_should_build_api_with_servers_bindings(
    fake_events_handler_cls, server_bindings_str, mocker,
):
    asyncapi.build_api_auto_spec(
        'asyncapi._tests', server_bindings=server_bindings_str
    )

    assert fake_events_handler_cls.call_args_list == [
        mocker.call(
            url='kafka://fake.fake',
            bindings={'option1': '0.1', 'option2': '0'},
        )
    ]


@pytest.mark.asyncio
async def test_should_publish_message(
    fake_api, fake_events_handler, fake_message, mocker, json_message
):
    await fake_api.publish('fake', fake_message)

    assert fake_events_handler.publish.call_args_list == [
        mocker.call(channel='fake', message=json_message.decode())
    ]


@pytest.mark.asyncio
async def test_should_listen_message(
    fake_api, fake_events_handler, fake_message, mocker
):
    fake_operation = asynctest.CoroutineMock()
    fake_api.operations[('fake', 'fake_operation')] = fake_operation
    await fake_api.listen('fake')

    assert fake_events_handler.subscribe.call_args_list == [
        mocker.call(channel='fake')
    ]
    assert fake_operation.call_args_list == [mocker.call(fake_message)]


@pytest.mark.asyncio
async def test_should_not_publish_for_invalid_channel(fake_api, fake_message):
    with pytest.raises(asyncapi.exceptions.InvalidChannelError) as exc_info:
        await fake_api.publish('faked', fake_message)

    assert exc_info.value.args == ('faked',)


@pytest.mark.asyncio
async def test_should_not_listen_for_invalid_channel(fake_api):
    with pytest.raises(asyncapi.exceptions.InvalidChannelError) as exc_info:
        await fake_api.listen('faked')

    assert exc_info.value.args == ('faked',)
