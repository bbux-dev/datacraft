import pytest
from datagen import SpecException
from datagen.utils import get_caster


def test_valid_key_forms():
    valid_names = ['cast']

    for name in valid_names:
        caster = get_caster({name: 'float'})
        assert caster is not None
        assert caster.cast('1.1') == 1.1


def test_none_is_none():
    caster = get_caster({'cast': None})
    assert caster is None


def test_valid_type_cast_forms1():
    input_value = '42.2'
    type_map = {
        'i': 42,
        'int': 42,
        'f': 42.2,
        'float': 42.2,
        's': input_value,
        'str': input_value,
        'string': input_value,
        'h': str(hex(42)),
        'hex': str(hex(42)),
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
        'h': str(hex(123)),
        'hex': str(hex(123))
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


def test_hex_cast_value_error():
    caster = get_caster({'cast': 'hex'})
    with pytest.raises(SpecException):
        caster.cast('abc123')


def test_castors_handle_lists():
    input_value = [1.1, 2.2, 3.3]
    type_map = {
        'i': [1, 2, 3],
        'int': [1, 2, 3],
        'f': [1.1, 2.2, 3.3],
        'float': [1.1, 2.2, 3.3],
        's': ['1.1', '2.2', '3.3'],
        'str': ['1.1', '2.2', '3.3'],
        'string': ['1.1', '2.2', '3.3'],
        'h': [str(hex(1)), str(hex(2)), str(hex(3))],
        'hex': [str(hex(1)), str(hex(2)), str(hex(3))],
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
