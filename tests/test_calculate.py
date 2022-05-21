import pytest

import datacraft
import datacraft.supplier.calculate

# to trigger registration

simple_calc_data = [
    (
        {'a': 2, 'b': 2},
        '{{a}} + {{b}} + 2',
        6
    ),
    (
        {'ft': [4, 5, 6]},
        '{{ft}} * 30.48',
        121.92
    ),
    (
        {'a': 3, 'b': 4, 'not_used': 43},
        'sqrt({{a}}*{{a}} + {{b}}*{{b}})',
        5.0
    ),
    (
        {'a': '3', 'b': '4'},
        'sqrt({{ a | int }}*{{ a | int }} + {{ b | int }}*{{ b | int }})',
        5.0
    )
]


@pytest.mark.parametrize('alias_to_values, formula, expected_first_value', simple_calc_data)
def test_simple_calculation(alias_to_values, formula, expected_first_value):
    mapping = {key: datacraft.suppliers.values(values) for key, values in alias_to_values.items()}

    supplier = datacraft.supplier.calculate._CalculateSupplier(mapping, datacraft.template_engines.string(formula))

    assert supplier.next(0) == expected_first_value


def test_calculate_valid_from_builder():
    spec_builder = datacraft.spec_builder()
    spec_builder.values('field', 21)
    mapping = {'field': 'a'}
    formula = '{{a}} * 2'
    spec_builder.calculate('meaning_of_life', fields=mapping, formula=formula)

    assert next(spec_builder.build().generator(1, enforce_schema=True))['meaning_of_life'] == 42.0


@pytest.mark.parametrize('keyword', ['for', 'if', 'else', 'in', 'elif'])
def test_keywords_are_now_valid(keyword):
    spec_builder = datacraft.spec_builder()
    spec_builder.values('field', 84)
    mapping = {'field': keyword}
    formula = '{{%s}}/2' % keyword
    spec_builder.calculate('meaning_of_life', fields=mapping, formula=formula)

    assert next(spec_builder.build().generator(1))['meaning_of_life'] == 42.0


missing_required_invalid_inputs = [
    (None, None, '{{ a }} + 2'),
    ({'not_used': 'a'}, {'not_used': 'a'}, '{{ a }} + 2'),
    (None, {'not_used': 'a'}, None),
    ({'not_used': 'a'}, None, None),
    ({}, None, '{{ a }} + 2'),
    (None, ['not_used', 'a'], '{{ a }} + 2')
]


@pytest.mark.parametrize('fields, refs, formula', missing_required_invalid_inputs)
def test_calculate_missing_required(fields, refs, formula):
    spec_builder = datacraft.spec_builder()
    spec_builder.calculate('something_interesting', fields=fields, refs=refs, formula=formula)

    with pytest.raises(datacraft.SpecException):
        next(spec_builder.build().generator(1))
