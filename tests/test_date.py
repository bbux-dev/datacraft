import re
from dataspec.loader import Loader
# need this to trigger type handler registration
from dataspec.type_handlers import date_handler


def test_basic_spec():
    spec = {"foo": {"type": "date"}}
    values = _get_unique_values(spec, 'foo')
    assert len(values) > 0


def test_date_delta():
    config = {"delta_days": 1}
    spec = {"foo": {"type": "date", "config": config}}
    values = _get_unique_values(spec, 'foo')
    # this should create three unique dates
    print(values)
    assert len(values) == 3


def test_date_anchor_positive_delta():
    config = {"delta_days": 1, "anchor": "02-01-2050"}
    spec = {"foo": {"type": "date", "config": config}}
    _test_date_spec(spec, 'foo', 100, ['01-01-2050', '02-01-2050', '03-01-2050'])


def test_date_anchor_negative_delta_string():
    config = {"delta_days": "-1", "anchor": "02-01-2050"}
    spec = {"foo": {"type": "date", "config": config}}
    _test_date_spec(spec, 'foo', 1000, ['01-01-2050', '02-01-2050', '03-01-2050'])


def test_delta_as_array():
    config = {"delta_days": [1, 2], "anchor": "02-01-2050"}
    spec = {"foo": {"type": "date", "config": config}}
    # expect one day behind and two days ahead
    _test_date_spec(spec, 'foo', 1000, ['01-01-2050', '02-01-2050', '03-01-2050', '03-01-2050'])


def test_date_anchor_format():
    config = {"delta_days": 1, "anchor": "02-Feb-2050", "format": "%d-%b-%Y"}
    spec = {"foo": {"type": "date", "config": config}}
    _test_date_spec(spec, 'foo', 100, ['01-Feb-2050', '02-Feb-2050', '03-Feb-2050'])


def test_date_anchor_format_iso():
    _test_date_anchor_format_iso_type('date.iso')


def test_date_anchor_format_iso_microseconds():
    _test_date_anchor_format_iso_type('date.iso.us')


def _test_date_anchor_format_iso_type(type_key):
    config = {"delta_days": 1, "anchor": "02-Feb-2050", "format": "%d-%b-%Y"}
    spec = {"foo": {"type": type_key, "config": config}}
    loader = Loader(spec)
    supplier = loader.get('foo')
    # only the date portion of the iso date
    values = list(set([_date_only(supplier.next(i)) for i in range(100)]))
    for instance in ['2050-02-01', '2050-02-02', '2050-02-03']:
        assert instance in values


def _date_only(iso_string):
    return iso_string.split('T')[0]


def test_date_offset():
    # anchored to 7 Feb - 5 day offset gives center of 2 Feb +- 1 day
    config = {"delta_days": 1, "anchor": "07-Feb-2050", "format": "%d-%b-%Y", "offset": 5}
    spec = {"foo": {"type": "date", "config": config}}
    _test_date_spec(spec, 'foo', 10, ['01-Feb-2050', '02-Feb-2050', '03-Feb-2050'])


def _test_date_spec(spec, key, iterations, expected):
    values = _get_unique_values(spec, key, iterations)
    for instance in expected:
        assert instance in values


def _get_unique_values(spec, key, iterations=100):
    loader = Loader(spec)
    supplier = loader.get(key)
    return list(set([supplier.next(i) for i in range(iterations)]))
