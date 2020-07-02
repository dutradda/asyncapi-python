import pytest

import asyncapi


@pytest.fixture(autouse=True)
def fake_yaml(mocker, spec_dict):
    yaml = mocker.patch.object(asyncapi, 'yaml')
    mocker.patch('asyncapi.open')
    yaml.safe_load.return_value = spec_dict
    return yaml


def test_should_get_api():
    api = asyncapi.api('fake')

    assert api.spec
    assert api.operations


def test_should_execute_fake_operation():
    api = asyncapi.api('fake')
    message = {'faked': True}

    assert api.fake_operation(message) == message
