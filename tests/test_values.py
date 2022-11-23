from collections import Counter

import pytest

import datacraft
from . import builder


def test_single_value():
    spec = {'type': 'values', 'data': 42}
    most_common_keys = _get_most_common_keys(spec, 10, 2)

    assert len(most_common_keys) == 1
    assert 42 in most_common_keys


def test_values_list():
    spec = {'data': [1, 2, 3, 4, 5]}
    most_common_keys = _get_most_common_keys(spec, 10, 10)

    assert len(most_common_keys) == 5
    assert [1, 2, 3, 4, 5] == most_common_keys


def test_weighted_values():
    spec = {'data': {'foo': 0.5, 'bar': 0.4, 'baz': 0.1}}
    most_common_keys = _get_most_common_keys(spec, 100, 2)

    assert 'foo' in most_common_keys
    assert 'bar' in most_common_keys


@pytest.mark.parametrize("null_marker_key", ['_NONE_', '_NULL_', '_NIL_'])
def test_weighted_values_special_none_marker(null_marker_key):
    spec = {'data': {'foo': 0.5, null_marker_key: 0.4, 'baz': 0.1}}
    most_common_keys = _get_most_common_keys(spec, 100, 2)

    assert 'foo' in most_common_keys
    assert None in most_common_keys


def test_weighted_boolean():
    weights = {
        "_TRUE_": 0.3,
        "_FALSE_": 0.7
    }
    spec = {
        "boolean_field": builder.values(data=weights)
    }
    values = [e['boolean_field'] for e in datacraft.entries(spec, 10)]
    assert all(v in [True, False] for v in values), "Not all values are boolean as expected"


def test_weighted_values_invalid_type():
    spec = {'foo': '0.5', 'bar': '0.4', 'baz': '0.1'}
    with pytest.raises(datacraft.SpecException):
        datacraft.suppliers.weighted_values(spec)


def test_weighted_values_empty():
    spec = {}
    with pytest.raises(datacraft.SpecException):
        datacraft.suppliers.weighted_values(spec)


def test_shortcut_notation():
    # not type or data key, just what would have been the value for the data key
    spec = builder.values({'foo': 0.5, 'bar': 0.4, 'baz': 0.1})
    most_common_keys = _get_most_common_keys(spec, 100, 2)

    assert 'foo' in most_common_keys
    assert 'bar' in most_common_keys


def _get_most_common_keys(spec, iterations, num_keys_to_collect):
    supplier = datacraft.suppliers.values(spec)
    data = [supplier.next(i) for i in range(iterations)]
    counter = Counter(data)
    most_common_keys = [item[0] for item in counter.most_common(num_keys_to_collect)]
    return most_common_keys


def test_count_param_invalid():
    # the word two is not a valid count
    spec = {'foo?count=two': ['A', 'B', 'C', 'D']}
    updated = datacraft.preprocess_spec(spec)
    with pytest.raises(ValueError):
        datacraft.suppliers.values(updated['foo'])


def _test_invalid_spec(spec, key):
    updated = datacraft.preprocess_spec(spec)
    with pytest.raises(datacraft.SpecException):
        datacraft.suppliers.values(updated[key])


def test_count_param_valid():
    spec = {
        'foo?count=2': ['A', 'B', 'C', 'D']
    }
    updated = datacraft.preprocess_spec(spec)
    supplier = datacraft.suppliers.values(updated['foo'])
    first = supplier.next(0)
    assert type(first) == list
    assert ['A', 'B'] == first


def test_config_ref_for_values():
    """ verifies that the values ref inherits the config from the config_ref """
    spec = builder.single_field("name?config_ref=quoteit", ["bob", "joe", "ann", "sue"]) \
        .add_ref("quoteit", builder.config_ref(quote="\"")) \
        .build()
    supplier = datacraft.loader.field_loader(spec).get('name')
    assert supplier.next(0) == '"bob"'


def test_values_list_order():
    data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    spec = builder.single_field('field', data).build()
    supplier = datacraft.loader.field_loader(spec).get('field')

    values = [supplier.next(i) for i in range(10)]
    assert values == data


def test_values_count_as_list():
    data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    spec = builder.single_field('field', builder.values(data, count=[2, 3])).build()
    supplier = datacraft.loader.field_loader(spec).get('field')

    first = supplier.next(0)
    assert isinstance(first, list) and len(first) == 2
    second = supplier.next(1)
    assert isinstance(second, list) and len(second) == 3
