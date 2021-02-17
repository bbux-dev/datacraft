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


def test_fields_specified_but_not_all_defined():
    spec = {
        "field:combine": {"fields": ["ONE", "TWO"]},
        "ONE": ["a", "b", "c"]
    }
    _test_invalid_combine_spec(spec)


def test_combine_list_no_refs_invalid():
    spec = {"field": {"type": "combine-list"}}
    _test_invalid_combine_spec(spec)


def test_combine_list_empty_refs_invalid():
    spec = {"field": {"type": "combine-list", "refs": []}}
    _test_invalid_combine_spec(spec)


def test_combine_list_single_list_refs_invalid():
    spec = {"field": {"type": "combine-list", "refs": ["ONE"]}, "refs": {"ONE": "uno"}}
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
    with pytest.raises(SpecException) as err:
        Loader(spec).get('field')
    # for debugging
    # print(str(err.value))


def test_combine_lists():
    s1 = suppliers.values({'data': ['a', 'b', 'c']})
    s2 = suppliers.values({'data': [1, 2, 3, 4, 5]})
    s3 = suppliers.values({'data': ['foo', 'bar', 'baz', 'bin', 'oof']})

    combo = suppliers.combine([s1, s2, s3], config={'join_with': ''})

    assert combo.next(0) == 'a1foo'
    assert combo.next(1) == 'b2bar'
    assert combo.next(2) == 'c3baz'


def test_combine_fields():
    spec = {
        "full_name:combine?join_with= ": {"fields": ["first", "last"]},
        "first": ["bob", "rob", "ann", "sue"],
        "last": ["smith", "jones", "frank", "wee"]
    }
    supplier = Loader(spec).get('full_name')
    assert supplier.next(0) == 'bob smith'


def test_combine_list_spec_valid_but_weird1():
    spec = {"field": {"type": "combine-list", "refs": [["ONE"]]}, "refs": {"ONE": "uno"}}
    supplier = Loader(spec).get('field')
    assert supplier.next(0) == 'uno'
    assert supplier.next(1) == 'uno'


def test_combine_list_spec_valid_but_weird2():
    spec = {"field": {"type": "combine-list", "refs": [["ONE", "TWO"]]}, "refs": {"ONE": "uno", "TWO": "dos"}}
    supplier = Loader(spec).get('field')
    assert supplier.next(0) == 'unodos'
    assert supplier.next(1) == 'unodos'


def test_combine_list_spec_valid_normal():
    spec = {
        "field": {
            "type": "combine-list",
            "refs": [
                ["ONE", "TWO"],
                ["TWO", "TRE"],
                ["TRE", "ONE"]
            ]
        },
        "refs": {
            "ONE": "uno",
            "TWO": "dos",
            "TRE": "tres"
        }
    }
    supplier = Loader(spec).get('field')
    assert supplier.next(0) == 'unodos'
    assert supplier.next(1) == 'dostres'
    assert supplier.next(2) == 'tresuno'
