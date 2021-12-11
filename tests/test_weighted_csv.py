import os

import pytest

import datacraft
# to trigger registration
from datacraft import cli

test_dir = os.sep.join([os.path.dirname(os.path.realpath(__file__)), 'data'])


def test_weighted_csv_valid_with_header_indexed_column():
    spec = _build_csv_spec('status', column=1, weight_column=2, headers=True)

    gen = spec.generator(3, data_dir=test_dir)

    val = next(gen)
    assert 'status' in val
    assert val['status'].isnumeric()


def test_weighted_csv_count_greater_than_one():
    spec = _build_csv_spec('status', column='status', weight_column='weight', headers='on', count=2)

    gen = spec.generator(3, data_dir=test_dir)

    val = next(gen)
    assert 'status' in val
    assert isinstance(val['status'], list)


def test_weighted_csv_valid_with_header_named_column():
    spec = _build_csv_spec('status', column='status', weight_column='weight', headers='on')

    gen = spec.generator(3, data_dir=test_dir)

    val = next(gen)
    assert 'status' in val
    assert val['status'].isnumeric()


def test_weighted_csv_valid_no_header_indexed_column():
    spec = _build_csv_spec('status', datafile="weighted_no_headers.csv", headers=False, column=1, weight_column=2)

    gen = spec.generator(1, data_dir=test_dir)

    val = next(gen)
    assert 'status' in val
    assert val['status'].isnumeric()


def test_weighted_csv_from_builder():
    spec = datacraft.spec_builder() \
        .weighted_csv('status', datafile='weighted.csv', column='status', weight_column='weight', headers=True) \
        .to_spec()

    gen = spec.generator(1, enforce_schema=True, data_dir=test_dir)

    val = next(gen)
    assert 'status' in val
    assert val['status'].isnumeric()


def test_weighted_csv_valid_invalid_indexed_column():
    spec = _build_csv_spec('status', column=0, weight_column=2, headers=True)

    gen = spec.generator(3, data_dir=test_dir)
    with pytest.raises(datacraft.SpecException):
        next(gen)


def _build_csv_spec(field_name, **config):
    base = {
        "datafile": "weighted.csv"
    }
    base.update(config)
    return datacraft.spec_builder() \
        .add_field(field_name, datacraft.builder.weighted_csv(**base)) \
        .build()
