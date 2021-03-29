import pytest
from dataspec import key_providers, SpecException


def test_invalid_fields_name():
    spec = {
        "one": ["uno", "ichi"],
        "two": ["dos", "ni"],
        "field_groups": {
            "one_two": {
                "weight": 1.0,
                "name_should_be_fields": ["one", "two"],
            }
        }
    }
    with pytest.raises(SpecException):
        key_providers.from_spec(spec).get()


def test_no_field_groups():
    spec = {
        "one": ["uno", "ichi"],
        "two": ["dos", "ni"],
    }
    provider = key_providers.from_spec(spec)

    assert _get_keys(provider) == ['one', 'two']


def test_list_of_fields():
    spec = {
        "one": ["uno", "ichi"],
        "two": ["dos", "ni"],
        "three": ["tres", "son"],
        "field_groups": [
            ["one"],
            ["one", "two"],
            ["one", "two", "three"]
        ]
    }
    provider = key_providers.from_spec(spec)

    assert _get_keys(provider) == ['one']
    assert _get_keys(provider) == ['one', 'two']
    assert _get_keys(provider) == ['one', 'two', 'three']


def _get_keys(provider):
    _, keys = provider.get()
    return keys


def test_weighted_field_groups():
    spec = {
        "one": ["uno", "ichi"],
        "two": ["dos", "ni"],
        "three": ["tres", "son"],
        "field_groups": {
            "groupA": {
                "weight": 0.7,
                "fields": ["one", "two"],
            },
            "groupB": {
                "weight": 0.3,
                "fields": ["one", "two", "three"]
            }
        }
    }
    provider = key_providers.from_spec(spec)
    for _ in range(100):
        field_group, keys = provider.get()
        assert field_group == 'groupA' or field_group == 'groupB'
        assert keys == ['one', 'two'] or keys == ['one', 'two', 'three']


def test_named_field_groups():
    spec = {
        "one": ["uno", "ichi"],
        "two": ["dos", "ni"],
        "three": ["tres", "son"],
        "field_groups": {
            "groupA": ["one", "two"],
            "groupB": ["one", "two", "three"]
        }
    }
    provider = key_providers.from_spec(spec)
    for _ in range(100):
        field_group, keys = provider.get()
        assert field_group == 'groupA' or field_group == 'groupB'
        assert keys == ['one', 'two'] or keys == ['one', 'two', 'three']