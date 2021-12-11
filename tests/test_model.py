import datacraft


def test_spec_acts_like_dictionary():
    raw = {
        "field": {"type": "uuid"}
    }

    spec = datacraft.DataSpec(raw)

    spec['key'] = ['a', 'b', 'c']
    assert 'key' in spec
    assert 'field' in spec

    spec.pop('field')
    assert 'field' not in spec

    del spec['key']
    assert 'key' not in spec

    # to get coverage for __repr__
    print(spec)
