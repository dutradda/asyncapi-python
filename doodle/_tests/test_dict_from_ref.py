import pytest

import doodle


@pytest.fixture
def spec():
    return {'fake1': {'fake2': {'fake3': {'faked': True}}}}


def test_should_get_dict_from_ref(spec):
    ref = '#/fake1/fake2/fake3'
    expected = {'faked': True}

    assert doodle.dict_from_ref(ref, spec) == expected


def test_should_not_get_dict_from_ref(spec):
    ref = '#/fake1/fake3'

    with pytest.raises(doodle.ReferenceNotFoundError):
        doodle.dict_from_ref(ref, spec)
