import decimal

import pytest

import datacraft
from . import builder


def test_random_range_exponent():
    value = datacraft.suppliers.random_range(-180.0, -90.0, 7).next(0)
    as_decimal = decimal.Decimal(str(value))
    assert as_decimal >= -180.0
    assert as_decimal <= -90.0
    assert as_decimal.as_tuple().exponent >= -7


valid_tests = [
    ("rand_range", [-180.0, -90.0], -180, -90),
    ("rand_int_range", [1.5, 5.5], 1, 6),
    ("integer", [1, 100], 1, 100),
    ("rand_range", [10.5], 0, 10.5),
    ("rand_range", [0.123000, 0.124999, 3], 0.123, 0.125),
]


@pytest.mark.parametrize("field_type,data,lower,upper", valid_tests)
def test_random_range_parameterized(field_type, data, lower, upper):
    spec_builder = builder.spec_builder()
    spec = spec_builder.add_field('test', {'type': field_type, 'data': data}).build()
    val = next(spec.generator(1, enforce_schema=True))['test']
    assert lower <= float(val) <= upper


field_type_keys = [
    "rand_range",
    "rand_int_range"
]


@pytest.mark.parametrize("field_type", field_type_keys)
def test_random_range_invalid_missing_data(field_type):
    with pytest.raises(datacraft.SpecException):
        spec_builder = builder.spec_builder()
        spec = spec_builder.add_field('test', {'type': field_type}).build()
        next(spec.generator(1))['test']


invalid_data_type = [
    ("rand_range", None),
    ("rand_int_range", {'foo': 'bar'}),
    ("rand_range", []),
    ("integer", "not-valid")
]


@pytest.mark.parametrize("field_type, data", invalid_data_type)
def test_random_range_invalid_data_type(field_type, data):
    with pytest.raises(datacraft.SpecException):
        spec_builder = builder.spec_builder()
        spec = spec_builder.add_field('test', {'type': field_type, 'data': data}).build()
        next(spec.generator(1))['test']
