import pytest

import asyncapi
import asyncapi.builder


@pytest.fixture(autouse=True)
def fake_jsonschema_asdataclass(mocker):
    return mocker.patch.object(asyncapi.builder, 'jsonschema_asdataclass')


@pytest.fixture
def expected_spec(fake_jsonschema_asdataclass):
    message = asyncapi.Message(
        name='Fake Message',
        title='Faked',
        summary='Faked message',
        content_type='application/json',
        payload=fake_jsonschema_asdataclass.return_value,
    )
    return asyncapi.Specification(
        info=asyncapi.Info(
            title='Fake API', version='0.0.1', description='Faked API',
        ),
        servers={
            'development': asyncapi.Server(
                name='development',
                url='fake.fake',
                protocol=asyncapi.ProtocolType.KAFKA,
                description='Fake Server',
            )
        },
        channels={
            'fake': asyncapi.Channel(
                name='fake',
                description='Fake Channel',
                subscribe=asyncapi.Operation(
                    operation_id='fake_operation', message=message,
                ),
            )
        },
        components=asyncapi.Components(
            messages={'FakeMessage': message},
            schemas={
                'FakePayload': {
                    'type': 'object',
                    'properties': {'faked': {'type': 'integer'}},
                }
            },
        ),
    )


@pytest.fixture
def expected_server_bindings_spec(expected_spec):
    expected_spec.servers['development'].bindings = {
        asyncapi.ProtocolType.KAFKA: {'option1': '0.1', 'option2': '0'}
    }
    return expected_spec


def test_should_build_spec(spec_dict, expected_spec):
    assert asyncapi.build_spec(spec_dict) == expected_spec


def test_should_build_spec_with_server_bindings(
    spec_dict_server_bindings, expected_server_bindings_spec
):
    assert (
        asyncapi.build_spec(spec_dict_server_bindings)
        == expected_server_bindings_spec
    )
