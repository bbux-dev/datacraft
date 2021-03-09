from dataspec import Loader, SpecException
from dataspec.type_handlers import char_class_handler
import pytest


def test_char_class_no_data_element():
    spec = {
        "name": {
            "type": "char_class",
            "config": {"count": 4}
        }
    }

    with pytest.raises(SpecException):
        Loader(spec).get('name')


def test_char_class_special_exclude():
    exclude = "&?!."
    spec = {
        "name": {
            "type": "char_class",
            "data": "special",
            "config": {
                "min": 1,
                "max": 5,
                "exclude": exclude
            }
        }
    }

    supplier = Loader(spec).get('name')

    for i in range(100):
        value = supplier.next(i)
        assert 1 <= len(value) <= 5
        for excluded in exclude:
            assert excluded not in value


def test_char_class_word():
    spec = {
        "name": {
            "type": "char_class",
            "data": "word",
            "config": {"count": 4}
        }
    }

    supplier = Loader(spec).get('name')

    for i in range(100):
        value = supplier.next(i)
        assert len(value) == 4


def test_char_class_stats_config():
    spec = {
        "name": {
            "type": "char_class",
            "data": "word",
            "config": {
                "stats_based_config": True,
                "mean": 5,
                "stddev": 2,
                "min": 3,
                "max": 8
            }
        }
    }

    supplier = Loader(spec).get('name')

    for i in range(100):
        value = supplier.next(i)
        assert 3 <= len(value) <= 8
