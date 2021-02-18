import pytest
from dataspec import SpecException
from dataspec.utils import get_caster


def test_valid_key_forms():
    valid_names = ['cast', 'cast_to', 'cast_as']

    for name in valid_names:
        caster = get_caster({name: 'float'})
        assert caster is not None
        assert caster.cast('1.1') == 1.1


def test_valid_type_cast_forms1():
    input_value = '42.2'
    type_map = {
        'i': 42,
        'int': 42,
        'f': 42.2,
        'float': 42.2,
        's': input_value,
        'str': input_value,
        'string': input_value
    }
    _test_valid_type_cast_forms(input_value, type_map)


def test_valid_type_cast_forms2():
    input_value = '123'
    type_map = {
        'i': 123,
        'int': 123,
        'f': 123.0,
        'float': 123.0,
        's': input_value,
        'str': input_value,
        'string': input_value
    }
    _test_valid_type_cast_forms(input_value, type_map)


def test_valid_type_cast_scientific_notation():
    input_value = '55e1'
    type_map = {
        'f': 550.0,
        'float': 550.0
    }
    _test_valid_type_cast_forms(input_value, type_map)


def test_valid_type_cast_int_weirdness():
    input_value = '171029091.0924891'
    type_map = {
        'i': 171029091,
        'int': 171029091
    }
    _test_valid_type_cast_forms(input_value, type_map)


def _test_valid_type_cast_forms(input_value, type_to_expected):
    for cast_type, expected_value in type_to_expected.items():
        caster = get_caster({'cast': cast_type})
        assert caster is not None
        assert caster.cast(input_value) == expected_value


def test_invalid_casting_int():
    with pytest.raises(SpecException):
        get_caster({'cast': 'int'}).cast('abc123')


def test_invalid_casting_float():
    with pytest.raises(SpecException):
        get_caster({'cast': 'float'}).cast('456def')
