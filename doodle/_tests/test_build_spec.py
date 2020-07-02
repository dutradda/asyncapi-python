import pytest

import doodle


@pytest.fixture
def expected_spec():
    message = doodle.Message(
        name='Fake Message',
        title='Faked',
        summary='Faked message',
        content_type='application/json',
        payload={
            'type': 'object',
            'properties': {'fake': {'type': 'boolean'}},
        },
    )
    return doodle.Specification(
        info=doodle.Info(
            title='Fake API', version='0.0.1', description='Faked API',
        ),
        servers=[
            doodle.Server(
                name='production',
                url='fake.fake',
                protocol=doodle.ProtocolType.KAFKA,
                description='Fake Server',
            )
        ],
        channels=[
            doodle.Channel(
                name='fake',
                description='Fake Channel',
                subscribe=doodle.Subscribe(
                    message, operation_id='doodle._tests.fake_operation'
                ),
            )
        ],
        components=doodle.Components(
            messages={'FakeMessage': message},
            schemas={'FakePayload': message.payload},
        ),
    )


def test_should_build_spec(spec_dict, expected_spec):
    assert doodle.build_spec(spec_dict) == expected_spec
