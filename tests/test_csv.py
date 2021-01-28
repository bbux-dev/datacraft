import os
import pytest
from dataspec.loader import Loader
from dataspec import SpecException
# need this to trigger registration
from dataspec.type_handlers import csv_handler
import dataspec.preprocessor

test_dir = f'{os.path.dirname(os.path.realpath(__file__))}/data'


# test data from https://wiki.splunk.com/Http_status.csv

def test_csv_valid_with_header_indexed_column():
    spec = _build_csv_spec('status', {})
    loader = Loader(spec, datadir=test_dir)
    supplier = loader.get('status')

    assert supplier.next(0) == '100'
    # last entry
    assert supplier.next(39) == '505'
    # verify wrap around
    assert supplier.next(40) == '100'


def test_csv_valid_no_header_indexed_column():
    spec = _build_csv_spec('status', {"datafile": "test_no_headers.csv", "headers": False})
    loader = Loader(spec, datadir=test_dir)
    supplier = loader.get('status')

    assert supplier.next(0) == '100'


def test_csv_valid_with_header_field_name_column():
    spec = _build_csv_spec('status', {"column": "status"})
    loader = Loader(spec, datadir=test_dir)
    supplier = loader.get('status')

    assert supplier.next(0) == '100'


def test_csv_valid_with_header_field_name_column_shorthand():
    spec = {"status_desc:csv?datafile=test.csv&headers=true&column=2": {}}
    loader = Loader(spec, datadir=test_dir)
    supplier = loader.get('status_desc')

    assert supplier.next(0) == 'Continue'


def test_invalid_csv_config_unknown_key():
    # column name should be status not status_code
    spec = _build_csv_spec('status', {"column": "status_code"})
    _test_invalid_csv_config('status', spec)


def _test_invalid_csv_config(key, spec):
    loader = Loader(spec)
    with pytest.raises(SpecException):
        loader.get(key)


def test_csv_single_column():
    # we don't specify the column number or name, so default is to expect single column of values
    spec = {"user_agent:csv?datafile=single_column.csv&headers=false": {}}
    loader = Loader(spec, datadir=test_dir)
    supplier = loader.get('user_agent')

    expected = 'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.1.2) Gecko/20090803 Firefox/3.5.2 Slackware'

    assert supplier.next(4) == expected



def _build_csv_spec(field_name, config_changes):
    base = {
        field_name: {
            "type": "csv",
            "config": {
                "datafile": "test.csv",
                "headers": True,
                "column": 1
            }
        }
    }
    base[field_name]['config'].update(config_changes)
    return base
