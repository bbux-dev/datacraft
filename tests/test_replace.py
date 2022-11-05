import pytest

import datacraft

from . import builder


def test_simple_replacement():
    spec = {
        "field": ["foo", "bar", "baz"],
        "replacement": builder.replace("field", {"ba": "fi"})
    }

    entries = datacraft.entries(spec, 3)
    values = [e['replacement'] for e in entries]
    assert values == ['foo', 'fir', 'fiz']


def test_regex_replacement():
    spec = {
        "field": ["val 1", "val 2", "val 3 1", "val 3 2"],
        "replacement": builder.regex_replace(ref="field", data={"\\s": "_"})
    }

    entries = datacraft.entries(spec, 4)
    values = [e['replacement'] for e in entries]
    assert values == ['val_1', 'val_2', 'val_3_1', 'val_3_2']


def _drop_key(data: dict, key_to_drop: str) -> dict:
    data.pop(key_to_drop, None)
    return data


bad_specs = [
    {
        "field": _drop_key(builder.replace("foo", {"foo": "bar"}), "ref")
    },
    {
        "field": _drop_key(builder.regex_replace("foo", {"foo": "bar"}), "data")
    },
]


@pytest.mark.parametrize("spec", bad_specs)
def test_missing_pieces(spec):
    # this does not use the schema for validation
    with pytest.raises(datacraft.SpecException) as err:
        datacraft.entries(spec, 1)
    assert "Failed to validate" not in str(err.value)


@pytest.mark.parametrize("spec", bad_specs)
def test_verify_schema(spec):
    # this call does
    with pytest.raises(datacraft.SpecException) as err:
        datacraft.entries(spec, 1, enforce_schema=True)
    assert "Failed to validate" in str(err.value)


bad_data_specs = [
    {
        "field": builder.replace("foo", ["foo", "bar"])
    },
    {
        "field": builder.regex_replace("foo", ("foo", "bar"))
    },
    {
        "field": builder.regex_replace("foo", {"foo", "bar"})
    },
]


@pytest.mark.parametrize("spec", bad_data_specs)
def test_data_is_wrong_type(spec):
    # this does not use the schema for validation
    with pytest.raises(datacraft.SpecException):
        datacraft.entries(spec, 1)


invalid_but_still_used_replacements = [
    1000,
    True,
    22.2
]


@pytest.mark.parametrize("replacement", invalid_but_still_used_replacements)
def test_invalid_but_still_used_replacements(replacement):
    spec = {
        "field": ["ba", "baba", "bababa"],
        "replacement": builder.replace("field", {"ba": replacement})
    }

    entries = datacraft.entries(spec, 3)
    values = [e['replacement'] for e in entries]
    assert all(isinstance(e, str) for e in values)
