import pytest

from datacraft.infer import (from_examples, _is_numeric, _calculate_weights,
                             _are_values_unique, _compute_range)


def test_is_numeric():
    assert _is_numeric([1, 2, 3])
    assert not _is_numeric([1, 2, '3'])
    assert not _is_numeric([True, 1, 2])


def test_calculate_weights():
    values = ["a", "b", "c", "a", "a", "b", "d", "a", "a", "a"]
    expected = {"a": 0.6, "b": 0.2, "c": 0.1, "d": 0.1}
    assert _calculate_weights(values) == expected


def test_are_values_unique():
    assert _are_values_unique([1, 2, 3, 4])
    assert not _are_values_unique([1, 2, 3, 4, 4])


def test_compute_int_range():
    values = [1, 5, 3, 4, 2]
    expected = {"type": "rand_int_range", "data": [1, 5]}
    assert _compute_range(values) == expected


def test_invalid_data_in_range():
    with pytest.raises(ValueError):
        _compute_range([1, 2, 3, 'a'])


def test_compute_float_range():
    values = [1.1, 5.1, 3.1, 4.1, 2.1]
    expected = {"type": "rand_range", "data": [1.1, 5.1]}
    assert _compute_range(values) == expected


def test_from_examples():
    examples = [
        {"foo": {"bar": 22.3, "baz": "single"}},
        {"foo": {"bar": 44.5, "baz": "double"}}
    ]
    expected = {
        'foo': {
            'type': 'nested',
            'fields': {
                'bar': {'type': 'rand_range', 'data': [22.3, 44.5]},
                'baz': {'type': 'values', 'data': ['single', 'double']}
            }
        }
    }
    assert from_examples(examples) == expected
