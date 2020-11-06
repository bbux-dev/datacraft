from datamaker.loader import Loader
from datamaker.exceptions import SpecException
import pytest


spec = {
    'foo': {
        'type': 'combine',
        'refs': ['ONE', 'TWO'],
        'config': {
            'join_with': ''
        }
    },
    'refs': {
        'ONE': { 'type': 'values', 'data': ['do', 'ca', 'pi']},
        'TWO': { 'type': 'values', 'data': ['g', 't', 'g']}
    }
}

spec_missing_type = {
    'foo': {
        'data': ['one', 'two', 'tre']
    }
}

spec_undefined_refs = {
    'foo': {
        'type': 'combine',
        'refs': ['ONE', 'TWO']
    }
}


def test_load_spec_invalid_key():
    loader = Loader(spec)
    with pytest.raises(SpecException):
        loader.get('unknown')


def test_load_spec_missing_type():
    loader = Loader(spec_missing_type)
    with pytest.raises(SpecException):
        loader.get('foo')


def test_load_spec_missing_type():
    loader = Loader(spec_missing_type)
    with pytest.raises(SpecException):
        loader.get('foo')


def test_load_spec_undefined_refs():
    loader = Loader(spec_undefined_refs)
    with pytest.raises(SpecException):
        loader.get('foo')


def test_load_spec_valid():
    loader = Loader(spec)
    supplier = loader.get('foo')

    assert supplier.next(0) == 'dog'
    assert supplier.next(1) == 'cat'
    assert supplier.next(2) == 'pig'
