from dataspec.loader import Loader
from dataspec.exceptions import SpecException
from collections import Counter
import pytest
# to trigger registration
from dataspec.type_handlers import combine, weighted_ref

spec = {
    'foo': {
        'type': 'combine',
        'refs': ['ONE', 'TWO'],
        'config': {
            'join_with': ''
        }
    },
    'refs': {
        'ONE': {'type': 'values', 'data': ['do', 'ca', 'pi']},
        'TWO': {'type': 'values', 'data': ['g', 't', 'g']}
    }
}


def test_load_spec_invalid_key():
    loader = Loader(spec)
    with pytest.raises(SpecException):
        loader.get('unknown')


def test_load_spec_missing_type_defaults_to_values():
    spec_missing_type = {
        'foo': {
            'data': ['one', 'two', 'tre']
        }
    }
    loader = Loader(spec_missing_type)
    supplier = loader.get('foo')

    assert supplier.next(0) == 'one'
    assert supplier.next(1) == 'two'
    assert supplier.next(2) == 'tre'


def test_load_spec_undefined_refs():
    spec_undefined_refs = {
        'foo': {
            'type': 'combine',
            'refs': ['ONE', 'TWO']
        }
    }
    loader = Loader(spec_undefined_refs)
    with pytest.raises(SpecException):
        loader.get('foo')


def test_load_spec_valid():
    loader = Loader(spec)
    supplier = loader.get('foo')

    assert supplier.next(0) == 'dog'
    assert supplier.next(1) == 'cat'
    assert supplier.next(2) == 'pig'


def test_load_spec_weighted_ref():
    weighted_ref_spec = {
        'foo': {
            'type': 'weightedref',
            "data": {
                "POSITIVE": 0.5,
                "NEGATIVE": 0.4,
                "NEUTRAL": 0.1
            }

        },
        'refs': {
            'POSITIVE': {'type': 'values', 'data': ['yes']},
            'NEGATIVE': {'type': 'values', 'data': ['no']},
            'NEUTRAL': {'type': 'values', 'data': ['meh']}
        }
    }
    loader = Loader(weighted_ref_spec)
    supplier = loader.get('foo')

    # expect mostly positive and negative values
    data = [supplier.next(i) for i in range(0, 100)]
    counter = Counter(data)
    # get the top two most common entries, which should be yes and no
    most_common_keys = [item[0] for item in counter.most_common(2)]

    assert 'yes' in most_common_keys
    assert 'no' in most_common_keys


def test_shortcut_notation_config_in_key():
    config_in_key_spec = {
        'foo?prefix=TEST': [1, 2, 3, 4, 5]
    }
    loader = Loader(config_in_key_spec)
    supplier = loader.get('foo')

    _verify_expected_values(supplier, 5, ['TEST1', 'TEST2', 'TEST3', 'TEST4', 'TEST5'])


def _verify_expected_values(supplier, iterations, expected_values):
    data = [supplier.next(i) for i in range(iterations)]
    assert data == expected_values
