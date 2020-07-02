import pytest


@pytest.fixture
def spec_dict():
    return {
        'info': {
            'title': 'Fake API',
            'version': '0.0.1',
            'description': 'Faked API',
        },
        'servers': {
            'production': {
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
                    'content_type': 'application/json',
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
