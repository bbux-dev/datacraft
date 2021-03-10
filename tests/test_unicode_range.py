import string
import pytest
from dataspec import Loader, SpecException
from dataspec.type_handlers import unicode_range


def test_unicode_no_data_element():
    spec = {"field": {"type": "unicode_range"}}
    with pytest.raises(SpecException):
        Loader(spec).get("field")


def test_unicode_data_is_not_list():
    spec = {"field": {"type": "unicode_range", "data": "0x3040,0x309f"}}
    with pytest.raises(SpecException):
        Loader(spec).get("field")


def test_unicode_range_single_range_as_hex():
    spec = {
        "text": {
            "type": "unicode_range",
            "data": [0x3040, 0x309f],
            "config": {
                "count": 5
            }
        }
    }
    supplier = Loader(spec).get('text')
    first = supplier.next(0)
    for c in first:
        assert 0x3040 <= ord(c) <= 0x309f


def test_unicode_range_single_range_as_hex_strings():
    spec = {
        "text": {
            "type": "unicode_range",
            "data": ['0x3040', '0x309f'],
            "config": {
                "mean": 5,
                "stddev": 2,
                "min": 2,
                "max": 7
            }
        }
    }
    supplier = Loader(spec).get('text')
    first = supplier.next(0)
    assert 2 <= len(first) <= 7
    for c in first:
        assert 0x3040 <= ord(c) <= 0x309f


def test_unicode_multiple_ranges():
    spec = {
        "text": {
            "type": "unicode_range",
            "data": [
                ['0x0590', '0x05ff'],
                ['0x3040', '0x309f']
            ],
            "config": {
                "min": 3,
                "max": 7
            }
        }
    }
    supplier = Loader(spec).get('text')
    first = supplier.next(0)
    assert 3 <= len(first) <= 7
    for c in first:
        assert 0x0590 <= ord(c) <= 0x05ff or 0x3040 <= ord(c) <= 0x309f
