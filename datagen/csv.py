"""
Module for csv related types
"""
import csv
import json
import logging
import os
from typing import Dict

# 250 MB
import datagen.supplier.common
from . import types, suppliers, schemas, utils
from .exceptions import SpecException
from .supplier.csv import CsvData, load_csv_data, csv_supplier


_ONE_MB = 1024 * 1024
_SMALL_ENOUGH_THRESHOLD = 250 * _ONE_MB

_log = logging.getLogger(__name__)

# to keep from reloading the same CsvData
_csv_data_cache: Dict[str, CsvData] = {}


@types.registry.types('csv')
def _configure_csv(field_spec, loader):
    """ Configures the csv value supplier for this field """
    config = utils.load_config(field_spec, loader)

    field_name = config.get('column', 1)
    sample = utils.is_affirmative('sample', config)
    count_supplier = suppliers.count_supplier_from_data(config.get('count', 1))

    csv_data = _load_csv_data(field_spec, config, loader.datadir)
    return csv_supplier(count_supplier, csv_data, field_name, sample)


@types.registry.schemas('csv')
def _get_csv_schema():
    """ get the schema for the csv type """
    return schemas.load('csv')


@types.registry.types('weighted_csv')
def _configure_weighted_csv(field_spec, loader):
    """ Configures the weighted_csv value supplier for this field """

    config = utils.load_config(field_spec, loader)

    field_name = config.get('column', 1)
    weight_column = config.get('weight_column', 2)
    count_supplier = suppliers.count_supplier_from_data(config.get('count', 1))

    datafile = config.get('datafile', types.get_default('csv_file'))
    csv_path = f'{loader.datadir}/{datafile}'
    has_headers = utils.is_affirmative('headers', config)
    numeric_index = isinstance(field_name, int)
    if numeric_index and field_name < 1:
        raise SpecException(f'Invalid index {field_name}, one based indexing used for column numbers')

    if has_headers and not numeric_index:
        choices = _read_named_column(csv_path, field_name)
        weights = _read_named_column_weights(csv_path, weight_column)
    else:
        choices = _read_indexed_column(csv_path, int(field_name), skip_first=numeric_index)
        weights = _read_indexed_column_weights(csv_path, int(weight_column), skip_first=numeric_index)
    return datagen.supplier.common.weighted_values_explicit(choices, weights, count_supplier)


@types.registry.schemas('weighted_csv')
def _get_weighted_csv_schema():
    """ get the schema for the weighted_csv type """
    return schemas.load('weighted_csv')


def _read_named_column(csv_path: str, column_name: str):
    """ reads values from a named column into a list """
    with open(csv_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        return [val[column_name] for val in reader]


def _read_named_column_weights(csv_path: str, column_name: str):
    """ reads values for weights for named column into a list """
    with open(csv_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        return [float(val[column_name]) for val in reader]


def _read_indexed_column(csv_path: str, column_index: int, skip_first: bool):
    """ reads values from a indexed column into a list """
    with open(csv_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        if skip_first:
            next(reader)
        return [val[column_index - 1] for val in reader]


def _read_indexed_column_weights(csv_path: str, column_index: int, skip_first: bool):
    """ reads values for weights for indexed column into a list """
    with open(csv_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        if skip_first:
            next(reader)
        return [float(val[column_index - 1]) for val in reader]


def _load_csv_data(field_spec, config, datadir):
    """
    Creates the CsvData object, caches the object by file path so that we can share this object across fields

    Args:
        field_spec: that triggered the creation
        config: to use to do the creation
        datadir: where to look for data files

    Returns:
        the configured CsvData object
    """
    datafile = config.get('datafile', types.get_default('csv_file'))
    csv_path = f'{datadir}/{datafile}'
    if csv_path in _csv_data_cache:
        return _csv_data_cache.get(csv_path)

    if not os.path.exists(csv_path):
        raise SpecException(f'Unable to locate data file: {datafile} in data dir: {datadir} for spec: '
                            + json.dumps(field_spec))
    delimiter = config.get('delimiter', ',')
    # in case tab came in as string
    if delimiter == '\\t':
        delimiter = '\t'
    quotechar = config.get('quotechar', '"')
    has_headers = utils.is_affirmative('headers', config)

    size_in_bytes = os.stat(csv_path).st_size
    max_csv_size = int(types.get_default('large_csv_size_mb')) * _ONE_MB
    sample_rows = utils.is_affirmative('sample_rows', config)
    buffer = size_in_bytes <= max_csv_size
    csv_data = load_csv_data(csv_path, delimiter, has_headers, quotechar, sample_rows, buffer)
    _csv_data_cache[csv_path] = csv_data
    return csv_data


