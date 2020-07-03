import pytest

import asyncapi


@pytest.fixture
def expected_spec():
    message = asyncapi.Message(
        name='Fake Message',
        title='Faked',
        summary='Faked message',
        content_type='application/json',
        payload={
            'type': 'object',
            'properties': {'faked': {'type': 'boolean'}},
        },
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
                subscribe=asyncapi.Subscribe(
                    message, operation_id='fake_operation'
                ),
            )
        },
        components=asyncapi.Components(
            messages={'FakeMessage': message},
            schemas={'FakePayload': message.payload},
        ),
    )


def test_should_build_spec(spec_dict, expected_spec):
    assert asyncapi.build_spec(spec_dict) == expected_spec
