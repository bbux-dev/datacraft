import pytest
from dataspec import builder, key_providers, SpecException


def test_invalid_fields_name():
    field_group = builder.weighted_field_group("one_two", fields=["not_defined", "not_defined_either"], weight=0.5)
    fields = field_group['one_two'].pop('fields')
    field_group['one_two']['wrong_name'] = fields

    spec = builder.Builder() \
        .add_fields(
        one=builder.values(["uno", "ichi"]),
        two=builder.values(["dos", "ni"])) \
        .add_field_group(field_group) \
        .to_spec()
    with pytest.raises(SpecException):
        key_providers.from_spec(spec).get()


def test_no_field_groups():
    spec = builder.Builder() \
        .add_fields(
        one=builder.values(["uno", "ichi"]),
        two=builder.values(["dos", "ni"])) \
        .to_spec()
    provider = key_providers.from_spec(spec)

    assert _get_keys(provider) == ['one', 'two']


def test_list_of_fields():
    field_groups = [
        ["one"],
        ["one", "two"],
        ["one", "two", "three"]
    ]
    spec = builder.Builder() \
        .add_fields(
        one=builder.values(["uno", "ichi"]),
        two=builder.values(["dos", "ni"])) \
        .add_field_groups(field_groups) \
        .to_spec()
    provider = key_providers.from_spec(spec)

    assert _get_keys(provider) == ['one']
    assert _get_keys(provider) == ['one', 'two']
    assert _get_keys(provider) == ['one', 'two', 'three']


def _get_keys(provider):
    _, keys = provider.get()
    return keys


def test_weighted_field_groups():
    field_groups = [
        builder.weighted_field_group("groupA", fields=["one", "two"], weight=0.7),
        builder.weighted_field_group("groupB", fields=["one", "two", "three"], weight=0.3),
    ]
    spec = builder.Builder() \
        .add_fields(
        one=builder.values(["uno", "ichi"]),
        two=builder.values(["dos", "ni"]),
        three=builder.values(["tres", "son"])) \
        .add_field_groups(field_groups) \
        .to_spec()

    provider = key_providers.from_spec(spec)
    for _ in range(100):
        field_group, keys = provider.get()
        assert field_group == 'groupA' or field_group == 'groupB'
        assert keys == ['one', 'two'] or keys == ['one', 'two', 'three']


def test_named_field_groups():
    field_groups = [
        builder.named_field_group("groupA", fields=["one", "two"]),
        builder.named_field_group("groupB", fields=["one", "two", "three"]),
    ]
    spec = builder.Builder() \
        .add_fields(
        one=builder.values(["uno", "ichi"]),
        two=builder.values(["dos", "ni"]),
        three=builder.values(["tres", "son"])) \
        .add_field_groups(field_groups) \
        .to_spec()

    provider = key_providers.from_spec(spec)
    for _ in range(100):
        field_group, keys = provider.get()
        assert field_group == 'groupA' or field_group == 'groupB'
        assert keys == ['one', 'two'] or keys == ['one', 'two', 'three']
