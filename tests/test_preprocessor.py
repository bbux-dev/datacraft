from dataspec.preprocessor import preprocess_spec, preprocess_csv_select
from dataspec.preprocessor import _parse_key
from dataspec import SpecException
import dataspec.suppliers as suppliers
import pytest


# hack to load up all types


def testpreprocess_spec_already_defined():
    config_in_key_spec = {
        'foo?prefix=TEST': [1, 2, 3, 4, 5],
        'foo': [5, 6, 7]
    }
    with pytest.raises(SpecException):
        preprocess_spec(config_in_key_spec)


def testpreprocess_spec_simple():
    config_in_key_spec = {
        'foo?prefix=TEST': [1, 2, 3, 4, 5],
    }
    updated = preprocess_spec(config_in_key_spec)
    assert 'foo' in updated


def testpreprocess_spec_uuid():
    config_in_key_spec = {"foo?level=5": {"type": "uuid"}}
    updated = preprocess_spec(config_in_key_spec)
    assert 'foo' in updated


def testpreprocess_spec_param_and_config():
    config_in_key_spec = {
        'bar?suffix=END': {
            'type': 'values',
            'data': [1, 2, 3, 4],
            'config': {'prefix': 'START'}
        }
    }
    updated = preprocess_spec(config_in_key_spec)
    assert 'bar' in updated
    spec = updated['bar']
    assert 'config' in spec
    config = spec['config']
    assert 'prefix' in config
    assert config['prefix'] == 'START'
    assert 'suffix' in config
    assert config['suffix'] == 'END'
    assert suppliers.is_decorated(spec)


def test_fully_inline_key_no_params():
    inline_key_spec = {"id:uuid": {}}
    updated = preprocess_spec(inline_key_spec)
    assert 'id' in updated


def test_fully_inline_key_with_params():
    config_in_key_spec = {"network:ip?cidr=2.3.4.0/14": {}}
    updated = preprocess_spec(config_in_key_spec)
    assert 'network' in updated
    spec = updated.get('network')
    assert 'type' in spec
    assert spec['type'] == 'ip'
    config = spec.get('config')
    assert config is not None


def test_fully_inline_key_no_params():
    config_in_key_spec = {"geo:geo.pair": {}}
    updated = preprocess_spec(config_in_key_spec)
    assert 'geo' in updated
    spec = updated.get('geo')
    assert 'type' in spec
    assert spec['type'] == 'geo.pair'
    config = spec.get('config')
    assert config is None


def test_weird_combos():
    spec = {
        "zero_to_ten?prefix=A-": {
            "type": "range",
            "data": [0, 10, 0.5],
            "config": {
                "prefix": "C-"
            }
        },
        "ztt:range?prefix=B-": [0, 10, 0.5]
    }

    updated = preprocess_spec(spec)
    assert 'zero_to_ten' in updated
    assert 'ztt' in updated

    zero_to_ten = updated['zero_to_ten']
    assert 'config' in zero_to_ten
    ztt = updated['ztt']
    assert 'config' in ztt

    # want to make sure params override configs
    assert 'A-' == zero_to_ten['config']['prefix']


def test_url_lib_parsing():
    format1 = "field?param=value"
    format2 = "user_agent:csv?datafile=single_column.csv&headers=false"

    newkey, spectype, params = _parse_key(format1)
    assert newkey == 'field'
    assert type(params) == dict
    assert spectype is None
    assert 'param' in params

    newkey, spectype, params = _parse_key(format2)
    assert newkey == 'user_agent'
    assert spectype == 'csv'
    assert params.get('datafile') == 'single_column.csv'


def test_url_lib_parsing_ignore_spaces():
    format1 = "short_name?    param=value"
    format2 = "aligned:values?prefix=foo& suffix=bar"

    _, _, params = _parse_key(format1)
    assert 'param' in params
    _, _, params = _parse_key(format2)
    assert 'suffix' in params


def test_preprocess_csv_select():
    spec = {
        "placeholder": {
            "type": "csv_select",
            "data": {
                "one": 1,
                "two": 2,
                "six": 6
            },
            "config": {
                "datafile": "not_real.csv",
                "headers": "no"
            }
        },
        "another:range": [1, 10]
    }

    updated = preprocess_csv_select(spec)
    for key in ['one', 'two', 'six', 'another']:
        assert key in updated
    assert 'placeholder' not in updated
    assert 'refs' in updated
    assert 'config' in updated['one'] and 'configref' in updated['one']['config']
