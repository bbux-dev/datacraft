from dataspec import Loader
from dataspec.type_handlers import nested_handler


def test_single_nested():
    spec = {
        "id:uuid": {},
        "geo": {
            "type": "nested",
            "fields": {
                "place_id:uuid": {},
                "coordinates": {
                    "type": "geo.pair",
                    "config": {
                        "as_list": True
                    }
                }
            }
        }
    }

    supplier = Loader(spec).get('geo')

    first = supplier.next(0)
    assert isinstance(first, dict)
    assert list(first.keys()) == ['place_id', 'coordinates']


def test_multi_nested():
    spec = {
        "id:uuid": {},
        "user:nested": {
            "fields": {
                "user_id:uuid": {},
                "geo": {
                    "type": "nested",
                    "fields": {
                        "place_id:uuid": {},
                        "coordinates": {
                            "type": "geo.pair",
                            "config": {
                                "as_list": True
                            }
                        }
                    }
                }
            }
        }
    }

    supplier = Loader(spec).get('user')

    first = supplier.next(0)
    assert isinstance(first, dict)
    assert list(first.keys()) == ['user_id', 'geo']

    second = first['geo']
    assert isinstance(second, dict)
    assert list(second.keys()) == ['place_id', 'coordinates']


def test_single_nested_as_array():
    spec = {
        "id:uuid": {},
        "geo": {
            "type": "nested",
            "config": {
                "as_array": "true"
            },
            "fields": {
                "place_id:uuid": {},
                "coordinates": {
                    "type": "geo.pair",
                    "config": {
                        "as_list": True
                    }
                }
            }
        }
    }

    supplier = Loader(spec).get('geo')

    first = supplier.next(0)
    assert isinstance(first, list)
    assert list(first[0].keys()) == ['place_id', 'coordinates']
