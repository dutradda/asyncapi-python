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
    fake_events_handler_cls, mocker, server_bindings_str,
):
    asyncapi.build_api('fake', server_bindings=server_bindings_str)

    assert fake_events_handler_cls.call_args_list == [
        mocker.call('kafka://fake.fake?option1=0.1&option2=0')
    ]


@pytest.mark.asyncio
async def test_should_build_api_with_channels_subscribers(
    mocker, spec_dict_publish
):
    api = asyncapi.build_api('fake', channels_subscribes='fake:fake_operation')

    assert api.spec.channels['fake'].publish
    assert api.spec.channels['fake'].subscribe.operation_id == 'fake_operation'


@pytest.mark.asyncio
async def test_should_build_api_with_channels_subscribers_new_channel(
    mocker, spec_dict_publish
):
    api = asyncapi.build_api(
        'fake', channels_subscribes='fake:fake-subscription=fake_operation'
    )

    assert api.spec.channels['fake'].publish
    assert not api.spec.channels['fake'].subscribe
    assert (
        api.spec.channels['fake-subscription'].subscribe.operation_id
        == 'fake_operation'
    )


@pytest.mark.asyncio
async def test_should_publish_message(
    spec_dict_publish,
    fake_api,
    fake_events_handler,
    fake_publish_message,
    mocker,
    json_message,
):
    await fake_api.publish('fake', fake_publish_message)

    assert fake_events_handler.publish.call_args_list == [
        mocker.call(channel='fake', message=json_message.decode())
    ]


@pytest.mark.asyncio
async def test_should_listen_message(
    fake_api, fake_events_handler, mocker, fake_message
):
    fake_operation = asynctest.CoroutineMock()
    fake_api.operations[('fake', 'fake_operation')] = fake_operation

    await fake_api.listen('fake')

    assert fake_events_handler.subscribe.call_args_list == [
        mocker.call(channel='fake')
    ]
    assert fake_operation.call_args_list == [mocker.call(fake_message)]


@pytest.mark.asyncio
async def test_should_not_publish_for_invalid_message(
    fake_api, fake_publish_message
):
    with pytest.raises(asyncapi.exceptions.InvalidMessageError) as exc_info:
        await fake_api.publish('fake', 'invalid')

    assert exc_info.value.args == ('invalid', type(fake_publish_message))


@pytest.mark.asyncio
async def test_should_not_publish_for_invalid_channel(
    fake_api, fake_publish_message
):
    with pytest.raises(asyncapi.exceptions.InvalidChannelError) as exc_info:
        await fake_api.publish('faked', fake_publish_message)

    assert exc_info.value.args == ('faked',)


@pytest.mark.asyncio
async def test_should_not_listen_for_invalid_message(
    fake_api,
    fake_events_handler,
    mocker,
    async_iterator,
    json_invalid_message,
):
    fake_operation = asynctest.CoroutineMock()
    fake_api.operations[('fake', 'fake_operation')] = fake_operation
    fake_events_handler.subscribe.return_value = async_iterator(
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
