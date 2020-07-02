import doodle


def test_should_fill_recursive_refs():
    spec = {
        'fake1': {'fake2': {'fake3': {'$ref': '#/fake3'}}},
        'fake3': {'$ref': '#/fake4'},
        'fake4': {'faked': True},
    }
    expected_spec = {
        'fake1': {'fake2': {'fake3': {'faked': True}}},
        'fake3': {'faked': True},
        'fake4': {'faked': True},
    }
    doodle.fill_refs(spec)
    assert spec == expected_spec


def test_should_fill_recursive_refs_2():
    spec = {
        'fake1': {'fake2': {'fake3': {'$ref': '#/fake3'}}},
        'fake3': {'fake4': {'$ref': '#/fake5'}},
        'fake5': {'faked': True},
    }
    expected_spec = {
        'fake1': {'fake2': {'fake3': {'fake4': {'faked': True}}}},
        'fake3': {'fake4': {'faked': True}},
        'fake5': {'faked': True},
    }
    doodle.fill_refs(spec)
    assert spec == expected_spec
