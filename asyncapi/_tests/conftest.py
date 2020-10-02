import asynctest
import orjson
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
                'publish': {
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
                    'properties': {'faked': {'type': 'integer'}},
                }
            },
        },
    }


@pytest.fixture
def spec_dict_publish(spec_dict):
    spec_dict['channels']['fake']['publish'] = spec_dict['channels'][
        'fake'
    ].pop('subscribe')
    return spec_dict


@pytest.fixture
def spec_dict_server_bindings(spec_dict):
    bindings = {'kafka': {'option1': '0.1', 'option2': '0'}}
    spec_dict['servers']['development']['bindings'] = bindings
    return spec_dict


@pytest.fixture
def server_bindings_str():
    return 'kafka:option1=0.1;option2=0'


@pytest.fixture(autouse=True)
def fake_yaml(mocker, spec_dict):
    yaml = mocker.patch.object(asyncapi.builder, 'yaml')
    mocker.patch('asyncapi.builder.open')
    yaml.safe_load.return_value = spec_dict
    return yaml


@pytest.fixture(autouse=True)
def fake_events_handler_cls(json_message, mocker, async_iterator):
    return mocker.patch.object(asyncapi.builder, 'EventsHandler')


@pytest.fixture(autouse=True)
def fake_events_handler(
    fake_events_handler_cls, json_message, mocker, async_iterator
):
    events_handler = fake_events_handler_cls.return_value
    events_handler.publish = asynctest.CoroutineMock()
    events_handler.connect = asynctest.CoroutineMock()
    events_handler.disconnect = asynctest.CoroutineMock()
    events_handler.subscribe.return_value = async_iterator(
        [mocker.MagicMock(message=json_message)]
    )
    return events_handler


@pytest.fixture
def fake_message(fake_api):
    return fake_api.spec.channels['fake'].subscribe.message.payload(1)


@pytest.fixture
def fake_publish_message(fake_api):
    return fake_api.spec.channels['fake'].publish.message.payload(1)


@pytest.fixture
def json_message():
    return orjson.dumps({'faked': 1})


@pytest.fixture
def json_invalid_message():
    return orjson.dumps({'faked': 'invalid'})


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
