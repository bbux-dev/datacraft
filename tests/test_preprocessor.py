import pytest

from datacraft import loader, SpecException
from datacraft.preprocessor import _parse_key, _is_spec_data, _update_no_params
from datacraft.preprocessor import _preprocess_spec, _preprocess_nested
from . import builder

parse_key_tests = [
    (
        "field?param=value",
        "field",
        None,
        {"param": "value"}
    ),
    (
        "short_name?    param=value",
        "short_name",
        None,
        {"param": "value"}
    ),
    (
        "aligned:values?prefix=foo& suffix=bar",
        "aligned",
        "values",
        {"prefix": "foo", "suffix": "bar"}
    ),
    (
        "user_agent:csv?datafile=single_column.csv&headers=false",
        "user_agent",
        "csv",
        {"datafile": "single_column.csv", "headers": "false"}
    )
]


@pytest.mark.parametrize("input_key,expected_key,expected_type,expected_params", parse_key_tests)
def test_parse_key(input_key, expected_key, expected_type, expected_params):
    newkey, spectype, params = _parse_key(input_key)
    assert newkey == expected_key
    assert spectype == expected_type
    assert params == expected_params


specs_should_raise_exception = [
    {'foo?prefix=TEST': [1, 2, 3, 4, 5],
     'foo': [5, 6, 7]},
    {"one": {"type": "range", "data": [0, 9]},
     "one?prefix=withparams": [1, 2, 3]}
]


@pytest.mark.parametrize("spec", specs_should_raise_exception)
def test_preprocess_should_raise_spec_exception(spec):
    with pytest.raises(SpecException):
        _preprocess_spec(spec)


default_transform_spec_tests = [
    (
        {'name': [1, 2, 3, 4, 5]},
        {'name': {'type': 'values', 'data': [1, 2, 3, 4, 5]}}
    ),
    (
        {'foo?prefix=TEST': [1, 2, 3, 4, 5]},
        {'foo': {'type': 'values', 'data': [1, 2, 3, 4, 5], 'config': {'prefix': 'TEST'}}}
    ),
    (
        {"foo:uuid": {}},
        {'foo': {'type': 'uuid'}}
    ),
    (
        {'bar?suffix=END': {'type': 'values', 'data': [1, 2, 3, 4], 'config': {'prefix': 'START'}}},
        {'bar': {'type': 'values', 'data': [1, 2, 3, 4], 'config': {'prefix': 'START', 'suffix': 'END'}}}
    ),
    (
        {'field_groups': [['one', 'two'], ['one', 'two', 'three']]},
        {'field_groups': [['one', 'two'], ['one', 'two', 'three']]}
    ),
    (
        {"network:ip?cidr=2.3.4.0/16": {}},
        {"network": {"type": "ip", "config": {"cidr": "2.3.4.0/16"}}}
    ),
    (
        {"geo:geo.pair": {}},
        {"geo": {"type": "geo.pair"}}
    ),
    (  # prefix in key overrides prefix in config for zero_to_ten
        {
            "zero_to_ten?prefix=A-": {"type": "range", "data": [0, 10, 0.5], "config": {"prefix": "C-"}},
            "ztt:range?prefix=B-": [0, 10, 0.5]
        },
        {
            "zero_to_ten": {"type": "range", "data": [0, 10, 0.5], "config": {"prefix": "A-"}},
            "ztt": {"type": "range", "data": [0, 10, 0.5], "config": {"prefix": "B-"}}
        }
    )
]


@pytest.mark.parametrize("input_spec,expected_output_spec", default_transform_spec_tests)
def test_preprocess_valid_specs(input_spec, expected_output_spec):
    updated = _preprocess_spec(input_spec)
    assert updated == expected_output_spec


csv_select_transform_tests = [
    (
        {
            "placeholder": {"type": "csv_select", "data": {"one": 1, "two": 2, "six": 6},
                            "config": {"datafile": "not_real.csv", "headers": "no"}},
            "another:range": [1, 10]
        },
        {
            "one": {"type": "csv", "config": {"column": 1, "config_ref": "placeholder_config_ref"}},
            "two": {"type": "csv", "config": {"column": 2, "config_ref": "placeholder_config_ref"}},
            "six": {"type": "csv", "config": {"column": 6, "config_ref": "placeholder_config_ref"}},
            "another": {"type": "range", "data": [1, 10]},
            "refs": {
                "placeholder_config_ref": {"type": "config_ref",
                                           "config": {"datafile": "not_real.csv", "headers": "no"}}
            }
        }
    ),
    (
        {
            "field:ref": "CSV_ONE",
            "refs": {
                "ONE": "Test Conflict",
                "CSV": {
                    "type": "csv_select",
                    "data": {"ONE": 1, "TWO": 2},
                    "config": {"datafile": "{{ injected }}"}
                }
            }
        },
        {
            "field": {"type": "ref", "data": "CSV_ONE"},
            "refs": {
                "ONE": {
                    "type": "values",
                    "data": "Test Conflict"
                },
                "CSV_CONFIG_REF": {
                    "type": "config_ref",
                    "config": {
                        "datafile": "{{ injected }}"
                    }
                },
                "ONE-1": {
                    "type": "csv",
                    "config": {
                        "column": 1,
                        "config_ref": "CSV_CONFIG_REF"
                    }
                },
                "TWO": {
                    "type": "csv",
                    "config": {
                        "column": 2,
                        "config_ref": "CSV_CONFIG_REF"
                    }
                }
            }
        }
    ),
    (
        {
            "field": {
                "type": "csv_select",
                "data": {
                    "ONE:float": 1,
                    "TWO": {"col": 2, "cast": "int"}
                },
                "config": {"datafile": "{{ the_name }}"}
            }
        },
        {
            "ONE": {
                "type": "csv",
                "config": {
                    "cast": "float",
                    "column": 1,
                    "config_ref": "field_config_ref"
                }
            },
            "TWO": {
                "type": "csv",
                "config": {
                    "cast": "int",
                    "column": 2,
                    "config_ref": "field_config_ref"
                }
            },
            "refs": {
                "field_config_ref": {
                    "type": "config_ref",
                    "config": {"datafile": "{{ the_name }}"}
                }
            },
        }
    )
]


@pytest.mark.parametrize("input_spec,expected_output_spec", csv_select_transform_tests)
def test_preprocess_csv_select(input_spec, expected_output_spec):
    # need first layer of pre-processing done
    updated = loader.preprocess_spec(input_spec)
    assert updated == expected_output_spec


specs_missing_config = [
    {"field": {"type": "csv_select", "data": {"ONE": 1, "TRE": 3}}},
    {"field": {"type": "csv_select", "data": {"ONE": 1, "TRE": 3}, "config": {}}},
]


@pytest.mark.parametrize("input_spec", specs_missing_config)
def test_preprocess_csv_select_missing_config(input_spec):
    with pytest.raises(SpecException):
        loader.preprocess_spec(input_spec)


def _builder_nested(outer_key, inner_key, inner_spec):
    """
    First part builds

    { innerkey: { some: spec } }

    Second part wraps first in

    { outerkey: { type: nested, fields: { innerkey: { some: spec } } } }
    """
    inner = builder.single_field(inner_key, inner_spec).build()
    return builder.single_field(outer_key, builder.nested(inner)).build()


nested_transform_tests = [
    (
        {
            "outer": {
                "type": "nested",
                "fields": {
                    "one:values": ["grey", "blue", "yellow"],
                    "two:range": [1, 10]
                }
            }
        },
        {
            "outer": {
                "type": "nested",
                "fields": {
                    "one": {"type": "values", "data": ["grey", "blue", "yellow"]},
                    "two": {"type": "range", "data": [1, 10]}
                }
            }
        }
    ),
    (
        {
            "outer:nested": {
                "fields": {
                    "placeholder": {"type": "csv_select", "data": {"one": 1, "two": 2, "six": 6},
                                    "config": {"datafile": "not_real.csv", "headers": "no"}}
                }
            },
            "another:range": [1, 10]
        },
        {
            "refs": {"placeholder_config_ref": {"type": "config_ref",
                                                "config": {"datafile": "not_real.csv", "headers": "no"}}},
            "outer": {
                "type": "nested",
                "fields": {
                    "one": {"type": "csv", "config": {"column": 1, "config_ref": "placeholder_config_ref"}},
                    "two": {"type": "csv", "config": {"column": 2, "config_ref": "placeholder_config_ref"}},
                    "six": {"type": "csv", "config": {"column": 6, "config_ref": "placeholder_config_ref"}}
                }
            },
            "another": {"type": "range", "data": [1, 10]},
        }
    ),
    (
        {
            "geo": {
                "type": "nested",
                "config": {"as_list": "true"},
                "fields": {"lat": 55.5, "long": 99.9}
            }
        }, {
            "geo": {
                "type": "nested",
                "config": {"as_list": "true"},
                "fields": {
                    "lat": {"type": "values", "data": 55.5},
                    "long": {"type": "values", "data": 99.9}
                }
            }
        },
    ),
    (
        {
            "one": {"type": "weighted_ref", "data": {"geo": 0.1}},
            "refs": {
                "geo": {
                    "type": "nested",
                    "config": {"as_list": "true"},
                    "fields": {
                        "lat": 55.5,
                        "long": 99.9
                    }
                }
            }
        },
        {
            "one": {"type": "weighted_ref", "data": {"geo": 0.1}},
            "refs": {
                "geo": {
                    "type": "nested",
                    "config": {"as_list": "true"},
                    "fields": {
                        "lat": {"type": "values", "data": 55.5},
                        "long": {"type": "values", "data": 99.9}
                    }
                }
            }
        }
    ),
    (
        _builder_nested('enemies', 'inner', ['bat', 'slime', 'orc']),
        _builder_nested('enemies', 'inner', builder.values(['bat', 'slime', 'orc'])).raw_spec,
    )
]


@pytest.mark.parametrize("input_spec,expected_output_spec", nested_transform_tests)
def test_preprocess_nested(input_spec, expected_output_spec):
    updated = _preprocess_spec(input_spec)
    updated = _preprocess_nested(updated)
    assert updated == expected_output_spec


def test_preprocess_nested_no_fields():
    spec = {
        "geo": {
            "type": "nested",
            "config": {"as_list": "true"},
            "refs": {"lat": 55.5, "long": 99.9}  # <- invalid should be fields
        }
    }
    with pytest.raises(SpecException):
        loader.preprocess_spec(spec)


def test_is_spec_data_positive_examples():
    examples = [
        1,
        'constant',
        25.5,
        ['a', 'b', 'c'],
        {'foo': 0.5, 'bar': 0.4, 'baz': 0.1}
    ]

    for example in examples:
        assert _is_spec_data(example, None)


def test_update_no_params():
    key = "field:nested"
    spec = {"id": {"type": "values", "data": [1, 2, 3]}}
    updated_specs = {}
    _update_no_params(key, spec, updated_specs)
    assert 'field' in updated_specs
    assert 'id' in updated_specs['field']
    assert 'nested' == updated_specs['field']['type']


def test_cnt_substitute_for_count():
    input_spec = {"id:cc-word?cnt=6": {}}
    updated = _preprocess_spec(input_spec)
    config = updated['id']['config']
    assert config.get('count') == '6'
    assert 'cnt' not in config
