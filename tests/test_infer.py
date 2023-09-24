import json

import pytest

from datacraft.infer import from_examples, csv_to_spec

from datacraft._infer import (_is_numeric, _calculate_weights,
                             _are_values_unique, _compute_range)

EXAMPLES = [
    # 0. Empty List
    ([], {}),

    # 1. Single Key-Value Pair
    ([{"key": "value"}], {"key": {"type": "values", "data": ["value"]}}),

    # 2. Different Data Types
    ([{"key1": 123, "key2": "string", "key3": 12.34, "key4": True, "key5": None}],
     {"key1": {"type": "values", "data": [123]},
      "key2": {"type": "values", "data": ["string"]},
      "key3": {"type": "values", "data": [12.34]},
      "key4": {"type": "values", "data": ["_TRUE_"]},
      "key5": {"type": "values", "data": ["_NONE_"]}}),

    # 3. Nested JSON
    ([{"parent": {"child1": "value1", "child2": "value2"}}],
     {"parent": {"type": "nested", "fields": {"child1": {"type": "values", "data": ["value1"]},
                                              "child2": {"type": "values", "data": ["value2"]}}}}),

    # 4. Lists in JSON
    ([{"key": [1, 2, 3]}],
     {'key': {'config': {'as_list': True, 'count': {'3': 1.0}}, 'data': [1, 3], 'type': 'rand_int_range'}}),

    # 5. Mixed Data in Lists (this one's tricky; adjust according to your function's behavior)
    ([{"key": [1, "two", 3.0]}], {"key": {"type": "values", "data": [[1, "two", 3.0]]}}),

    # 6. Varying Nested Depth
    ([{"key1": {"key2": {"key3": {"key4": "value"}}}}],
     {"key1": {"type": "nested", "fields": {"key2": {"type": "nested", "fields": {
         "key3": {"type": "nested", "fields": {"key4": {"type": "values", "data": ["value"]}}}}}}}}),

    # 7. Inconsistent Data Types (assuming your function captures both data types)
    ([{"key": "value"}, {"key": 123}], {"key": {"type": "values", "data": ["value", 123]}}),

    # 8. Boolean and None Handling
    ([{"key1": True, "key2": False, "key3": None}],
     {"key1": {"type": "values", "data": ["_TRUE_"]},
      "key2": {"type": "values", "data": ["_FALSE_"]},
      "key3": {"type": "values", "data": ["_NONE_"]}}),

    # 9. Larger Lists
    ([{"key": list(range(100))}], {'key': {'type': 'rand_int_range',
                                           'data': [0, 99],
                                           'config': {'as_list': True, 'count': {'100': 1.0}}
                                           }}),

    # 10. Overlapping and Non-overlapping Keys
    ([{"key1": "value1"}, {"key2": "value2"}],
     {"key1": {"type": "values", "data": ["value1"]}, "key2": {"type": "values", "data": ["value2"]}}),

    # 11. Special Characters in Keys
    ([{"key with space": "value", "key_with_underscore": 123, "!@#$%^&*()": "special"}],
     {"key with space": {"type": "values", "data": ["value"]},
      "key_with_underscore": {"type": "values", "data": [123]},
      "!@#$%^&*()": {"type": "values", "data": ["special"]}}),

    # 12. Very Large Numbers and Small Floats
    ([{"key1": 12345678901234567890, "key2": 0.000000123456}],
     {"key1": {"type": "values", "data": [12345678901234567890]},
      "key2": {"type": "values", "data": [0.000000123456]}})
]


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


def test_from_example_simple():
    examples = [
        {"bar": 22.3, "baz": "single"},
        {"bar": 44.5, "baz": "double"}
    ]
    expected = {
        'bar': {'type': 'rand_range', 'data': [22.3, 44.5]},
        'baz': {'type': 'values', 'data': ['single', 'double']}
    }
    assert from_examples(examples) == expected


def test_from_examples_nested():
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


def test_from_examples_list_value():
    examples = [
        {"bar": 22.3, "baz": [1, 2]},
        {"bar": 44.5, "baz": [3, 4, 5]}
    ]
    expected = {
        'bar': {'type': 'rand_range', 'data': [22.3, 44.5]},
        'baz': {
            'type': 'rand_int_range',
            'data': [1, 5],
            'config': {
                'count': {'2': 0.5, '3': 0.5},
                'as_list': True
            }
        }
    }
    assert from_examples(examples) == expected


@pytest.fixture
def sample_csv_file(tmpdir):
    data = """foo,bar,baz
1,22.3,single
2,44.5,double
3,44.6,triple"""

    file_path = tmpdir.join("sample.csv")
    with open(file_path, 'w') as f:
        f.write(data)
    return file_path


def test_csv_to_spec(sample_csv_file):
    result = csv_to_spec(sample_csv_file)

    expected = {
        'bar': {
            'type': 'rand_range',
            'data': [22.3, 44.6]
        },
        'baz': {
            'type': 'values',
            'data': ['single', 'double', 'triple']
        },
        'foo': {
            'type': 'rand_int_range',
            'data': [1, 3]
        }
    }

    assert result == expected


@pytest.mark.parametrize("input_data, expected_output", EXAMPLES)
def test_from_examples(input_data, expected_output):
    actual = from_examples(input_data)
    assert actual == expected_output, f"Actual not equal to expected: {json.dumps(actual, indent=2)}, " \
                                      f"{json.dumps(expected_output, indent=2)}"
