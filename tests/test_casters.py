import pytest

from datacraft import SpecException
from datacraft.casters import from_config


def test_valid_key_forms():
    valid_names = ['cast']

    for name in valid_names:
        caster = from_config({name: 'float'})
        assert caster is not None
        assert caster.cast('1.1') == 1.1


def test_none_is_none():
    caster = from_config({'cast': None})
    assert caster is None


def test_hex_cast_value_error():
    caster = from_config({'cast': 'hex'})
    with pytest.raises(SpecException):
        caster.cast('abc123')


forty_two_point_two = '42.2'
one_two_three = '123'
five_five_e_1 = '55e1'
large_decimal = '171029091.0924891'
float_list = [1.1, 2.2, 3.3]
space_aBcD_space = " aBcD "
five_point_one_to_nine = 5.123456789

cast_tests = [
    (forty_two_point_two, 'i', 42),
    (forty_two_point_two, 'int', 42),
    (forty_two_point_two, 'f', 42.2),
    (forty_two_point_two, 'float', 42.2),
    (forty_two_point_two, 's', forty_two_point_two),
    (forty_two_point_two, 'str', forty_two_point_two),
    (forty_two_point_two, 'string', forty_two_point_two),
    (forty_two_point_two, 'h', str(hex(42))),
    (forty_two_point_two, 'hex', str(hex(42))),
    (forty_two_point_two, 'l', forty_two_point_two),
    (forty_two_point_two, 'lower', forty_two_point_two),
    (forty_two_point_two, 'u', forty_two_point_two),
    (forty_two_point_two, 'upper', forty_two_point_two),

    (one_two_three, 'i', 123),
    (one_two_three, 'int', 123),
    (one_two_three, 'f', 123.0),
    (one_two_three, 'float', 123.0),
    (one_two_three, 's', one_two_three),
    (one_two_three, 'h', str(hex(123))),
    (one_two_three, 'hex', str(hex(123))),
    (one_two_three, 'lower', one_two_three),
    (one_two_three, 'upper', one_two_three),

    (five_five_e_1, 'f', 550.0),
    (five_five_e_1, 'float', 550.0),
    (five_five_e_1, 'l', five_five_e_1),
    (five_five_e_1, 'lower', five_five_e_1),
    (five_five_e_1, 'u', '55E1'),
    (five_five_e_1, 'upper', '55E1'),

    (large_decimal, 'i', 171029091),
    (large_decimal, 'int', 171029091),

    (float_list, 'i', [1, 2, 3]),
    (float_list, 'int', [1, 2, 3]),
    (float_list, 'f', [1.1, 2.2, 3.3]),
    (float_list, 'float', [1.1, 2.2, 3.3]),
    (float_list, 's', ['1.1', '2.2', '3.3']),
    (float_list, 'str', ['1.1', '2.2', '3.3']),
    (float_list, 'string', ['1.1', '2.2', '3.3']),
    (float_list, 'h', [str(hex(1)), str(hex(2)), str(hex(3))]),
    (float_list, 'hex', [str(hex(1)), str(hex(2)), str(hex(3))]),
    (float_list, 'l', ['1.1', '2.2', '3.3']),
    (float_list, 'lower', ['1.1', '2.2', '3.3']),
    (float_list, 'u', ['1.1', '2.2', '3.3']),
    (float_list, 'upper', ['1.1', '2.2', '3.3']),

    (space_aBcD_space, 'lower', ' abcd '),
    (space_aBcD_space, 'upper', ' ABCD '),
    (space_aBcD_space, 'trim', 'aBcD'),
    (space_aBcD_space, 'l;t', 'abcd'),
    (space_aBcD_space, 'u;t', 'ABCD'),
    (space_aBcD_space, 'trim;lower', 'abcd'),
    (space_aBcD_space, 'trim;str;upper;lower', 'abcd'),

    (five_point_one_to_nine, 'round', 5),
    (five_point_one_to_nine, 'round7', 5.1234568),
    (five_point_one_to_nine, 'round6', 5.123457),
    (five_point_one_to_nine, 'round5', 5.12346),
    (five_point_one_to_nine, 'round4', 5.1235),
    (five_point_one_to_nine, 'round3', 5.123),
    (five_point_one_to_nine, 'round2', 5.12),
    (five_point_one_to_nine, 'round1', 5.1),
    (five_point_one_to_nine, 'round0', 5.0),
]


@pytest.mark.parametrize("input_value, cast_type, expected_value", cast_tests)
def test_valid_type_cast_forms(input_value, cast_type, expected_value):
    caster = from_config({'cast': cast_type})
    assert caster is not None
    assert caster.cast(input_value) == expected_value


def test_invalid_casting_int():
    with pytest.raises(SpecException):
        from_config({'cast': 'int'}).cast('abc123')


def test_invalid_casting_float():
    with pytest.raises(SpecException):
        from_config({'cast': 'float'}).cast('456def')
