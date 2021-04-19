import re
from dataspec.loader import Loader
from dataspec import builder
# need this to trigger type handler registration
from dataspec.type_handlers import date_handler


def test_basic_spec():
    spec = _date_spec()
    values = _get_unique_values(spec, 'foo')
    assert len(values) > 0


def test_date_delta():
    spec = _date_spec(delta_days=1)
    values = _get_unique_values(spec, 'foo')
    # this should create three unique dates
    assert len(values) == 3


def test_date_anchor_positive_delta():
    config = {"delta_days": 1, "anchor": "02-01-2050"}
    spec = _date_spec(**config)
    _test_date_spec(spec, 'foo', 100, ['01-01-2050', '02-01-2050', '03-01-2050'])


def test_date_anchor_negative_delta_string():
    config = {"delta_days": "-1", "anchor": "02-01-2050"}
    spec = _date_spec(**config)
    _test_date_spec(spec, 'foo', 1000, ['01-01-2050', '02-01-2050', '03-01-2050'])


def test_delta_as_list():
    config = {"delta_days": [1, 2], "anchor": "02-01-2050"}
    spec = _date_spec(**config)
    # expect one day behind and two days ahead
    _test_date_spec(spec, 'foo', 1000, ['01-01-2050', '02-01-2050', '03-01-2050', '03-01-2050'])


def test_date_anchor_format():
    config = {"delta_days": 1, "anchor": "02-Feb-2050", "format": "%d-%b-%Y"}
    spec = _date_spec(**config)
    _test_date_spec(spec, 'foo', 100, ['01-Feb-2050', '02-Feb-2050', '03-Feb-2050'])


def test_date_anchor_format_iso():
    config = {"delta_days": 1, "anchor": "02-Feb-2050", "format": "%d-%b-%Y"}
    spec = _date_iso_spec(**config)
    _test_date_anchor_format_iso_type(spec)


def test_date_anchor_format_iso_microseconds():
    config = {"delta_days": 1, "anchor": "02-Feb-2050", "format": "%d-%b-%Y"}
    spec = _date_iso_us_spec(**config)
    _test_date_anchor_format_iso_type(spec)


def _test_date_anchor_format_iso_type(spec):
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
    spec = _date_spec(**config)
    _test_date_spec(spec, 'foo', 100, ['01-Feb-2050', '02-Feb-2050', '03-Feb-2050'])


def _test_date_spec(spec, key, iterations, expected):
    values = _get_unique_values(spec, key, iterations)
    for instance in expected:
        assert instance in values


def _get_unique_values(spec, key, iterations=100):
    loader = Loader(spec)
    supplier = loader.get(key)
    return list(set([supplier.next(i) for i in range(iterations)]))


def _date_spec(**config):
    return builder.Builder().add_field('foo', builder.date(**config)).build()


def _date_iso_spec(**config):
    return builder.Builder().add_field('foo', builder.date_iso(**config)).build()


def _date_iso_us_spec(**config):
    return builder.Builder().add_field('foo', builder.date_iso_us(**config)).build()


def test_date_range():
    spec = {
        'type': 'date_range',
        'config': {
            'join_with': '-',
            'format': '%Y%m%d',
            'offset': 365,
            'duration_days': 730
        }
    }
    spec = builder.spec_builder().add_field('single_date_range', spec).build()

    loader = Loader(spec)

    supplier = loader.get('single_date_range')

    date_range = supplier.next(0)

    assert len(date_range) == 17


def test_date_range_rand():
    spec = {
        'type': 'date_range',
        'config': {
            'join_with': '-',
            'format': '%Y%m%d',
            "rand_offset": [30, 90],
            "rand_duration_days": [30, 90]
        }
    }
    spec = builder.spec_builder().add_field('rand_date_range', spec).build()

    loader = Loader(spec)

    supplier = loader.get('rand_date_range')

    date_range = supplier.next(0)
    print(date_range)
    assert len(date_range) == 17
