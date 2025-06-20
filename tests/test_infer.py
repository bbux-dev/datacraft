import math
import json

import pytest

import datacraft
from datacraft.infer import from_examples, csv_to_spec, infer_csv_select

from datacraft._infer.helpers import (all_is_numeric, calculate_weights, are_values_unique)
from datacraft._infer.num_analyzers import compute_range

from .test_utils import deep_sort

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
    assert all_is_numeric([1, 2, 3])
    assert not all_is_numeric([1, 2, '3'])
    assert not all_is_numeric([True, 1, 2])


def test_calculate_weights():
    values = ["a", "b", "c", "a", "a", "b", "d", "a", "a", "a"]
    expected = {"a": 0.6, "b": 0.2, "c": 0.1, "d": 0.1}
    assert calculate_weights(values) == expected


def test_are_values_unique():
    assert are_values_unique([1, 2, 3, 4])
    assert not are_values_unique([1, 2, 3, 4, 4])


def test_compute_int_range():
    values = [1, 5, 3, 4, 2]
    expected = {"type": "rand_int_range", "data": [1, 5]}
    assert compute_range(values) == expected


def test_invalid_data_in_range():
    with pytest.raises(ValueError):
        compute_range([1, 2, 3, 'a'])


def test_compute_float_range():
    values = [1.1, 5.1, 3.1, 4.1, 2.1]
    expected = {"type": "rand_range", "data": [1.1, 5.1]}
    assert compute_range(values) == expected


def test_from_example_simple():
    examples = [
        {"bar": 22.3, "baz": "single"},
        {"bar": 44.5, "baz": "double"}
    ]
    expected = {
        'bar': {'type': 'rand_range', 'data': [22.3, 44.5]},
        'baz': {'type': 'values', 'data': ['single', 'double']}
    }
    assert deep_sort(from_examples(examples)) == deep_sort(expected)


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
    assert deep_sort(from_examples(examples)) == deep_sort(expected)


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

    assert deep_sort(result) == deep_sort(expected)


def test_infer_csv_select(sample_csv_file):
    result = infer_csv_select(sample_csv_file)
    
    expected = {
        "placeholder": {
            "type": "csv_select",
            "data": {
                "foo": 1,
                "bar": 2,
                "baz": 3
            },
            "config": {
                "datafile": "sample.csv",
                "headers": True,
            }
        }
    }
    
    assert result == expected


@pytest.mark.parametrize("input_data, expected_output", EXAMPLES)
def test_from_examples(input_data, expected_output):
    actual = from_examples(input_data)
    assert deep_sort(actual) == deep_sort(expected_output), f"Actual not equal to expected:" \
                                                            f" {json.dumps(actual, indent=2)}, " \
                                                            f"{json.dumps(expected_output, indent=2)}"


def test_round_trip():
    weights = {
        "a": 0.25,
        1: 0.25,
        "_TRUE_": 0.25,
        2.34567: 0.25
    }
    spec = {
        "basket": {
            "type": "values",
            "data": weights
        }
    }
    records = datacraft.entries(spec, 10000)
    inferred_spec = datacraft.infer.from_examples(records)

    for key, val in inferred_spec["basket"]["data"].items():
        assert math.isclose(weights[key], val, rel_tol=0.1)


@pytest.mark.parametrize(
    "input_str, expected_spec", [
        ("12-05-2020", {"type": "date"}),
        ("2020-05-12T14:20:30", {"type": "date.iso"}),
        ("2020-05-12T14:20:30.123", {"type": "date.iso.ms"}),
        ("2020-05-12T14:20:30.123456", {"type": "date.iso.us"}),
    ]
)
def test_infer_dates(input_str, expected_spec):
    records = [{"date": input_str}]
    inferred_spec = datacraft.infer.from_examples(records)
    assert "date" in inferred_spec
    assert inferred_spec["date"] == expected_spec


def test_infer_dates_multiple_formats():
    records = [
        {"ts": "2020-05-12T14:20:30"},
        {"ts": "2020-05-12T14:20:30.123456"}
    ]
    inferred_spec = datacraft.infer.from_examples(records)
    assert "ts" in inferred_spec
    assert inferred_spec["ts"]["type"] == "weighted_ref"


@pytest.mark.parametrize(
    "input_str, expected_spec", [
        ("192.168.1.1", {"type": "ip", "config": {"base": "192.168.1"}}),
        ("10.0.0.1", {"type": "ip", "config": {"base": "10.0.0"}}),
        ("00:1A:2B:3C:4D:5E", {"type": "net.mac"}),
        ("00-1A-2B-3C-4D-5E", {"type": "net.mac"}),
    ]
)
def test_infer_network_types(input_str, expected_spec):
    records = [{"network": input_str}]
    inferred_spec = datacraft.infer.from_examples(records)
    assert "network" in inferred_spec
    assert inferred_spec["network"] == expected_spec


def test_infer_invalid_ip():
    records = [{"network": "111.222.333.444"}]
    inferred_spec = datacraft.infer.from_examples(records)
    assert "network" in inferred_spec
    assert inferred_spec["network"]["type"] != "ip"


def test_infer_nested():
    records = [
        {
            "outer": {
                "ip": "192.168.1.1",
                "ts": "2020-05-12T14:20:30"
            }
        }
    ]
    inferred_spec = datacraft.infer.from_examples(records)
    assert "outer" in inferred_spec
    assert inferred_spec["outer"]["type"] == "nested"


def test_infer_nested_list():
    records = [
        {
            "outer": [
                {
                    "ip": "192.168.1.1",
                    "ts": "2020-05-12T14:20:30"
                }
            ]
        }
    ]
    inferred_spec = datacraft.infer.from_examples(records)
    assert "outer" in inferred_spec
    outer = inferred_spec["outer"]
    assert outer["type"] == "nested"
    assert "as_list" in outer["config"]
    assert outer["config"]["as_list"] is True


def test_infer_empty_lists():
    records = [
        {"list": []},
        {"list": []},
        {"list": []},
        {"list": []},
    ]
    inferred_spec = datacraft.infer.from_examples(records)
    assert "list" in inferred_spec
    field_spec = inferred_spec["list"]
    assert field_spec["type"] == "values"
