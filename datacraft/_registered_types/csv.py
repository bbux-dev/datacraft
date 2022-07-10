"""module for csv type datacraft registry functions"""
import csv
import json
import logging
import os

import datacraft
from datacraft.supplier.common import weighted_values_explicit
from . import schemas

_log = logging.getLogger(__name__)
_CSV_TYPE = 'csv'
_WEIGHTED_CSV = 'weighted_csv'
_CSV_EXAMPLE = {
    "status": {
        "type": "csv",
        "config": {
            "column": 1,
            "config_ref": "tabs_config"
        }
    },
    "description": {
        "type": "csv",
        "config": {
            "column": 2,
            "config_ref": "tabs_config"
        }
    },
    "status_type:csv?config_ref=tabs_config&column=3": {},
    "refs": {
        "tabs_config": {
            "type": "config_ref",
            "config": {
                "datafile": "tabs.csv",
                "delimiter": "\\t",
                "headers": True,
                "sample_rows": True
            }
        }
    }
}
_WEIGHTED_CSV_EXAMPLE = {
    "cities": {
        "type": "weighted_csv",
        "config": {
            "datafile": "weighted_cities.csv"
        }
    }
}


@datacraft.registry.types(_CSV_TYPE)
def _configure_csv(field_spec, loader):
    """ Configures the csv value supplier for this field """
    config = datacraft.utils.load_config(field_spec, loader)
    datafile = config.get('datafile', datacraft.registries.get_default('csv_file'))
    csv_path = f'{loader.datadir}/{datafile}'
    if not os.path.exists(csv_path):
        raise datacraft.SpecException(f'Unable to locate data file: {datafile} in data dir: {loader.datadir} for spec: '
                                      + json.dumps(field_spec))
    return datacraft.suppliers.csv(csv_path, **config)


@datacraft.registry.schemas(_CSV_TYPE)
def _get_csv_schema():
    """ get the schema for the csv type """
    return schemas.load(_CSV_TYPE)


@datacraft.registry.types(_WEIGHTED_CSV)
def _configure_weighted_csv(field_spec, loader):
    """ Configures the weighted_csv value supplier for this field """

    config = datacraft.utils.load_config(field_spec, loader)

    field_name = config.get('column', 1)
    weight_column = config.get('weight_column', 2)
    count_supplier = datacraft.suppliers.count_supplier(**config)

    datafile = config.get('datafile', datacraft.registries.get_default('csv_file'))
    csv_path = f'{loader.datadir}/{datafile}'
    has_headers = datacraft.utils.is_affirmative('headers', config)
    numeric_index = isinstance(field_name, int)
    if numeric_index and field_name < 1:
        raise datacraft.SpecException(f'Invalid index {field_name}, one based indexing used for column numbers')

    if has_headers and not numeric_index:
        choices = _read_named_column(csv_path, field_name)
        weights = _read_named_column_weights(csv_path, weight_column)
    else:
        choices = _read_indexed_column(csv_path, int(field_name), skip_first=numeric_index)
        weights = _read_indexed_column_weights(csv_path, int(weight_column), skip_first=numeric_index)
    return weighted_values_explicit(choices, weights, count_supplier)


@datacraft.registry.schemas(_WEIGHTED_CSV)
def _get_weighted_csv_schema():
    """ get the schema for the weighted_csv type """
    return schemas.load(_WEIGHTED_CSV)


@datacraft.registry.usage(_CSV_TYPE)
def _example_csv_usage():
    formatted_spec = datacraft.preprocess_and_format(_CSV_EXAMPLE)
    return f'Example Spec:\n{formatted_spec}'


@datacraft.registry.usage(_WEIGHTED_CSV)
def _example_weighted_csv_usage():
    formatted_spec = datacraft.preprocess_and_format(_WEIGHTED_CSV_EXAMPLE)
    return f'Example Spec:\n{formatted_spec}'


def _read_named_column(csv_path: str, column_name: str):
    """ reads values from a named column into a list """
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        return [val[column_name] for val in reader]


def _read_named_column_weights(csv_path: str, column_name: str):
    """ reads values for weights for named column into a list """
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        return [float(val[column_name]) for val in reader]


def _read_indexed_column(csv_path: str, column_index: int, skip_first: bool):
    """ reads values from a indexed column into a list """
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        if skip_first:
            next(reader)
        return [val[column_index - 1] for val in reader]


def _read_indexed_column_weights(csv_path: str, column_index: int, skip_first: bool):
    """ reads values for weights for indexed column into a list """
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        if skip_first:
            next(reader)
        return [float(val[column_index - 1]) for val in reader]
