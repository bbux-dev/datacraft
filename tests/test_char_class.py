import string

import pytest

import datacraft
from datacraft._registered_types.char_class import _CLASS_MAPPING
from . import builder


def test_char_class_no_data_element():
    spec = _char_class_spec(data="special", count=4)
    spec['name'].pop('data')

    with pytest.raises(datacraft.SpecException):
        datacraft.loader.field_loader(spec).get('name')


def test_char_class_special_exclude():
    exclude = "&?!."
    spec = _char_class_spec(data="special", min=1, max=5, exclude=exclude)

    supplier = datacraft.loader.field_loader(spec).get('name')
    _verify_values(supplier, 1, 5, exclude)


def test_char_class_word():
    spec = _char_class_spec(data="special", count=4)

    supplier = datacraft.loader.field_loader(spec).get('name')
    _verify_values(supplier, 4, 4)


def test_char_class_stats_config():
    spec = _char_class_spec(data="word", mean=5, stddev=2, min=3, max=8)

    supplier = datacraft.loader.field_loader(spec).get('name')
    _verify_values(supplier, 3, 8)


def test_char_class_printable():
    spec = _cc_abbrev_spec(abbrev="printable", mean=3, stddev=2, min=1, max=5)

    supplier = datacraft.loader.field_loader(spec).get('name')
    _verify_values(supplier, 1, 5)


def test_char_class_abbreviations():
    abbreviations = ['cc-' + key for key in _CLASS_MAPPING.keys()]

    for abbreviation in abbreviations:
        spec = _cc_abbrev_spec(abbrev=abbreviation, count=7)

        supplier = datacraft.loader.field_loader(spec).get('name')
        _verify_values(supplier, 7, 7)


def test_char_class_multiple_classes():
    exclude = "CUSTOM"
    spec = _char_class_spec(data=["lower", "digits", "CUSTOM"], exclude=exclude)

    supplier = datacraft.loader.field_loader(spec).get('name')
    value = supplier.next(0)
    assert isinstance(value, str)
    for char in value:
        assert char in string.ascii_lowercase or char in string.digits


def test_verify_class_mappings():
    for key, values in _CLASS_MAPPING.items():
        spec = _cc_abbrev_spec(f"cc-{key}", count=5)
        single_item = datacraft.entries(spec, 1)[0]['name']
        for c in single_item:
            assert c in values, f'{c} not expected to be part of {key} type. values: {values}'


def _verify_values(supplier, min_size, max_size, exclude='', iterations=100):
    for i in range(iterations):
        value = supplier.next(i)
        assert min_size <= len(value) <= max_size
        for excluded in exclude:
            assert excluded not in value


def _char_class_spec(data, **config):
    return builder.spec_builder() \
        .add_field("name", builder.char_class(data=data, **config)) \
        .build()


def _cc_abbrev_spec(abbrev, **config):
    return builder.spec_builder() \
        .add_field("name", builder.char_class_abbrev(cc_abbrev=abbrev, **config)) \
        .build()
