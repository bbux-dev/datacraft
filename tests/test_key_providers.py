import pytest

import datagen.suppliers
from datagen import builder, key_providers, SpecException


def test_no_field_groups():
    spec = one_two_builder().build()
    provider = key_providers.from_spec(spec)

    assert _get_keys(provider) == ['one', 'two']


def test_list_of_fields():
    field_groups = [
        ["one"],
        ["one", "two"],
        ["one", "two", "three"]
    ]

    spec_builder = one_two_three_builder()
    spec_builder.add_field_groups(field_groups),
    spec = spec_builder.build()
    provider = key_providers.from_spec(spec)

    assert _get_keys(provider) == ['one']
    assert _get_keys(provider) == ['one', 'two']
    assert _get_keys(provider) == ['one', 'two', 'three']


def _get_keys(provider):
    _, keys = provider.get()
    return keys


def test_weighted_field_groups():
    spec_builder = one_two_three_builder()
    spec_builder.weighted_field_group(weight=0.7, fields=["one", "two"])
    spec_builder.weighted_field_group(weight=0.3, fields=["one", "two", "three"]),
    spec = spec_builder.build()

    provider = key_providers.from_spec(spec)
    for _ in range(100):
        field_group, keys = provider.get()
        assert field_group == '0.7' or field_group == '0.3'
        assert keys == ['one', 'two'] or keys == ['one', 'two', 'three']


def test_weighted_field_groups_invalid_name():
    field_groups = {'one': ['A', 'B', 'C']}
    key_provider = key_providers.WeightedGroupKeyProvider(field_groups, datagen.suppliers.values(['uno']))
    # for coverage
    with pytest.raises(SpecException):
        key_provider.get()


def test_weighted_field_groups_invalid_type():
    # for coverage
    with pytest.raises(ValueError):
        key_providers._create_rotating_lists_key_provider('one,two,three')


def test_named_field_groups():
    spec_builder = one_two_three_builder()
    spec_builder.named_field_group(key="groupA", fields=["one", "two"])
    spec_builder.named_field_group(key="groupB", fields=["one", "two", "three"]),
    spec = spec_builder.build()

    provider = key_providers.from_spec(spec)
    for _ in range(100):
        field_group, keys = provider.get()
        assert field_group == 'groupA' or field_group == 'groupB'
        assert keys == ['one', 'two'] or keys == ['one', 'two', 'three']


def one_two_three_builder():
    spec_builder = one_two_builder()
    spec_builder.values('three', ["tres", "son"])
    return spec_builder


def one_two_builder():
    spec_builder = builder.Builder()
    spec_builder.values('one', ["uno", "ichi"])
    spec_builder.values('two', ["dos", "ni"])
    return spec_builder
