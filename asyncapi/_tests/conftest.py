import asynctest
import pytest

import asyncapi.builder


@pytest.fixture
def spec_dict():
    return {
        'info': {
            'title': 'Fake API',
            'version': '0.0.1',
            'description': 'Faked API',
        },
        'servers': {
            'development': {
                'url': 'fake.fake',
                'protocol': 'kafka',
                'description': 'Fake Server',
            }
        },
        'channels': {
            'fake': {
                'description': 'Fake Channel',
                'subscribe': {
                    'operationId': 'fake_operation',
                    'message': {'$ref': '#/components/messages/FakeMessage'},
                },
            }
        },
        'components': {
            'messages': {
                'FakeMessage': {
                    'name': 'Fake Message',
                    'title': 'Faked',
                    'summary': 'Faked message',
                    'contentType': 'application/json',
                    'payload': {'$ref': '#/components/schemas/FakePayload'},
                }
            },
            'schemas': {
                'FakePayload': {
                    'type': 'object',
                    'properties': {'faked': {'type': 'boolean'}},
                }
            },
        },
    }


@pytest.fixture(autouse=True)
def fake_yaml(mocker, spec_dict):
    yaml = mocker.patch.object(asyncapi.builder, 'yaml')
    mocker.patch('asyncapi.builder.open')
    yaml.safe_load.return_value = spec_dict
    return yaml


@pytest.fixture(autouse=True)
def fake_broadcast(message, mocker, async_iterator):
    broadcast = mocker.patch.object(asyncapi.builder, 'Broadcast').return_value
    broadcast.publish = asynctest.CoroutineMock()
    broadcast.connect = asynctest.CoroutineMock()
    broadcast.subscribe.return_value = async_iterator(
        [mocker.MagicMock(message=message)]
    )
    return broadcast


@pytest.fixture
def message():
    return {'faked': True}


@pytest.fixture
def invalid_message():
    return {'faked': 'invalid'}


@pytest.fixture
def async_iterator(mocker):
    return AsyncIterator


class AsyncIterator:
    def __init__(self, seq):
        self.iter = iter(seq)

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            return next(self.iter)
        except StopIteration:
            raise StopAsyncIteration

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        ...
