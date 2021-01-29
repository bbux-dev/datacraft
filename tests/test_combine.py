import pytest
from dataspec.loader import Loader
import dataspec.suppliers as suppliers
from dataspec import SpecException
# to trigger registration


def test_neither_refs_nor_fields_specified():
    spec = {"field:combine": {}}
    _test_invalid_combine_spec(spec)


def test_refs_specified_but_not_defined():
    spec = {"field:combine": {"refs": ["ONE", "TWO"]}}
    _test_invalid_combine_spec(spec)


def test_refs_specified_but_not_all_defined():
    spec = {
        "field:combine": {"refs": ["ONE", "TWO"]},
        "refs": {
            "ONE": ["a", "b", "c"]
        }
    }
    _test_invalid_combine_spec(spec)


def test_refs_specified_but_invalid_type():
    spec = {
        "field:combine": {"refs": ["ONE", "TWO"]},
        "refs": {
            "ONE": ["a", "b", "c"],
            "TWO:configref": {
                "config": {
                    "prefix": "foo",
                    "suffix": "@foo.bar"
                }
            }
        }
    }
    _test_invalid_combine_spec(spec)


def _test_invalid_combine_spec(spec):
    with pytest.raises(SpecException):
        Loader(spec).get('field')


def test_combine_lists():
    s1 = suppliers.values({'data': ['a', 'b', 'c']})
    s2 = suppliers.values({'data': [1, 2, 3, 4, 5]})
    s3 = suppliers.values({'data': ['foo', 'bar', 'baz', 'bin', 'oof']})

    combo = suppliers.combine([s1, s2, s3], config={'join_with': ''})

    assert combo.next(0) == 'a1foo'
    assert combo.next(1) == 'b2bar'
    assert combo.next(2) == 'c3baz'
