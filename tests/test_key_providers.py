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

    assert provider.get() == ['one', 'two']


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

    assert provider.get() == ['one']
    assert provider.get() == ['one', 'two']
    assert provider.get() == ['one', 'two', 'three']


def test_weighted_field_groups():
    spec = {
        "one": ["uno", "ichi"],
        "two": ["dos", "ni"],
        "three": ["tres", "son"],
        "field_groups": {
            "one_two": {
                "weight": 0.7,
                "fields": ["one", "two"],
            },
            "one_two_three": {
                "weight": 0.3,
                "fields": ["one", "two", "three"]
            }
        }
    }
    provider = key_providers.from_spec(spec)
    for _ in range(100):
        keys = provider.get()
        assert keys == ['one', 'two'] or keys == ['one', 'two', 'three']
