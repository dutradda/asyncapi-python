import asynctest
import pytest
from jsondaora import DeserializationError

import asyncapi.exceptions


@pytest.fixture
def fake_api():
    return asyncapi.build_api('fake', module_name='asyncapi._tests')


@pytest.fixture
def fake_api_no_operation():
    return asyncapi.build_api('fake')


@pytest.fixture
def fake_api_no_operation_id(spec_dict):
    spec_dict['channels']['fake']['subscribe'].pop('operationId')
    return asyncapi.build_api('fake')


def test_should_get_api(fake_api):
    assert fake_api.spec
    assert fake_api.operations


@pytest.mark.asyncio
async def test_should_build_api_with_servers_bindings(
    fake_broadcast_cls, mocker, server_bindings_str,
):
    asyncapi.build_api('fake', server_bindings=server_bindings_str)

    assert fake_broadcast_cls.call_args_list == [
        mocker.call('kafka://fake.fake?option1=0.1&option2=0')
    ]


@pytest.mark.asyncio
async def test_should_publish_message(
    fake_api, fake_broadcast, fake_message, mocker, json_message
):
    await fake_api.publish('fake', fake_message)

    assert fake_broadcast.publish.call_args_list == [
        mocker.call(channel='fake', message=json_message.decode())
    ]


@pytest.mark.asyncio
async def test_should_listen_message(
    fake_api, fake_broadcast, mocker, fake_message
):
    fake_operation = asynctest.CoroutineMock()
    fake_api.operations[('fake', 'fake_operation')] = fake_operation

    await fake_api.listen('fake')

    assert fake_broadcast.subscribe.call_args_list == [
        mocker.call(channel='fake')
    ]
    assert fake_operation.call_args_list == [mocker.call(fake_message)]


@pytest.mark.asyncio
async def test_should_not_publish_for_invalid_message(fake_api, fake_message):
    with pytest.raises(asyncapi.exceptions.InvalidMessageError) as exc_info:
        await fake_api.publish('fake', 'invalid')

    assert exc_info.value.args == ('invalid', type(fake_message))


@pytest.mark.asyncio
async def test_should_not_publish_for_invalid_channel(fake_api, fake_message):
    with pytest.raises(asyncapi.exceptions.InvalidChannelError) as exc_info:
        await fake_api.publish('faked', fake_message)

    assert exc_info.value.args == ('faked',)


@pytest.mark.asyncio
async def test_should_not_listen_for_invalid_message(
    fake_api, fake_broadcast, mocker, async_iterator, json_invalid_message,
):
    fake_operation = asynctest.CoroutineMock()
    fake_api.operations[('fake', 'fake_operation')] = fake_operation
    fake_broadcast.subscribe.return_value = async_iterator(
        [mocker.MagicMock(message=json_invalid_message)]
    )

    with pytest.raises(DeserializationError) as exc_info:
        await fake_api.listen('fake')

    assert exc_info.value.args == (
        'Invalid type=typing.Union[int, NoneType] for field=faked',
    )
    assert not fake_operation.called


@pytest.mark.asyncio
async def test_should_not_listen_for_invalid_channel(fake_api):
    with pytest.raises(asyncapi.exceptions.InvalidChannelError) as exc_info:
        await fake_api.listen('faked')

    assert exc_info.value.args == ('faked',)


@pytest.mark.asyncio
async def test_should_not_listen_for_operation_error(fake_api_no_operation):
    with pytest.raises(
        asyncapi.exceptions.OperationIdNotFoundError
    ) as exc_info:
        await fake_api_no_operation.listen('fake')

    assert exc_info.value.args == ('fake_operation',)


@pytest.mark.asyncio
async def test_should_not_listen_for_operation_id_error(
    fake_api_no_operation_id,
):
    with pytest.raises(
        asyncapi.exceptions.ChannelOperationNotFoundError
    ) as exc_info:
        await fake_api_no_operation_id.listen('fake')

    assert exc_info.value.args == ('fake',)
