import pytest

import datacraft.registries as types
import datacraft
from datacraft._registered_types.schemas import load
from datacraft.schemas import validate_schema_for_spec


def test_load_unknown_key():
    with pytest.raises(datacraft.ResourceError):
        load('fluffy')


def test_load_valid():
    for type_name in ['range']:
        _test_load_valid(type_name)


def _test_load_valid(type_name):
    schema = load(type_name)
    assert schema is not None
    assert isinstance(schema, dict) is True


def test_lookup_from_registry():
    for type_name in ['range']:
        _test_lookup_from_registry(type_name)


def _test_lookup_from_registry(type_name):
    schema = types.lookup_schema(type_name)
    assert schema is not None
    assert isinstance(schema, dict) is True


def test_load_and_validate_schema():
    range_schema = types.lookup_schema('range')
    validate_schema_for_spec('range', {'type': 'range', 'data': [0, 10]}, range_schema)


def test_load_and_validate_invalid_schema():
    range_schema = types.lookup_schema('range')
    with pytest.raises(datacraft.SpecException):
        validate_schema_for_spec('range', {'type': 'range'}, range_schema)


def test_invalid_count_param_values_spec():
    values_schema = types.lookup_schema('values')
    with pytest.raises(datacraft.SpecException):
        spec = {'type': 'values', 'data': [1, 2, 3], 'config': {'count': {}}}
        validate_schema_for_spec('values', spec, values_schema)
