import asyncapi


def test_should_build_api_from_http_yaml():
    assert asyncapi.api('http://localhost:9080/api.yaml')
