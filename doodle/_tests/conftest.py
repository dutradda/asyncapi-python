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
                    'operationId': 'doodle._tests.fake_operation',
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
                    'properties': {'fake': {'type': 'boolean'}},
                }
            },
        },
    }
