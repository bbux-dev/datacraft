"""
Uses external csv file to supply data

csv
---

Prototype:

.. code-block:: python

    {
      "<field name>": {
        "type": "csv",
        "config": {
          "datafile": "filename in datedir",
          "headers": "yes, on, true for affirmative",
          "column": "1 based column number or field name if headers are present",
          "delimiter": "how values are separated, default is comma",
          "quotechar": "how values are quoted, default is double quote",
          "sample": "If the values should be selected at random, default is false",
          "count": "Number of values in column to use for value"
        }
      }
    }

Examples:

.. code-block:: json

    {
      "cities": {
        "type": "csv",
        "config": {
          "datafile": "cities.csv",
          "delimiter": "~",
          "sample": true
        }
      }
    }

.. code-block:: json

    {
      "status": {
        "type": "csv",
        "config": {
          "column": 1,
          "configref": "tabs_config"
        }
      },
      "description": {
        "type": "csv",
        "config": {
          "column": 2,
          "configref": "tabs_config"
        }
      },
      "status_type:csv?configref=tabs_config&column=3": {},
      "refs": {
        "tabs_config": {
          "type": "configref",
          "config": {
            "datafile": "tabs.csv",
            "delimiter": "\t",
            "headers": true
          }
        }
      }
    }

csv_select
----------

Prototype:

.. code-block:: python

    {
      "<field name>": {
        "type": "csv_select",
        "data": {"<field_one>": <1 based column index for field 1>, ..., "<field n>": }
        "config": {
          "datafile": "filename in datedir",
          "headers": "yes, on, true for affirmative",
          "delimiter": "how values are separated, default is comma",
          "quotechar": "how values are quoted, default is double quote"
        }
      }
    }

Examples:

.. code-block:: json

    {
      "placeholder": {
        "type": "csv_select",
        "data": {"geonameid": 1, "name": 2, "latitude": 5, "longitude": 6, "country_code": 9, "population": 15},
        "config": {
          "datafile": "allCountries.txt",
          "headers": false,
          "delimiter": "\t"
        }
      }
    }


weighted_csv
------------

Prototype:

.. code-block:: python

    {
      "<field name>": {
        "type": "weighted_csv",
        "config": {
          "datafile": "filename in datedir",
          "headers": "yes, on, true for affirmative",
          "column": "1 based column number or field name if headers are present",
          "weight_column": "1 based column number or field name if headers are present where weights are defined"
          "delimiter": "how values are separated, default is comma",
          "quotechar": "how values are quoted, default is double quote",
          "sample": "If the values should be selected at random, default is false",
          "count": "Number of values in column to use for value"
        }
      }
    }

Examples:

.. code-block:: json

    {
      "cities": {
        "type": "weighted_csv",
        "config": {
          "datafile": "weighted_cities.csv"
        }
      }
    }
"""
import csv
import json
import os
import random
from typing import Dict
from typing import Union

import datagen

# 250 MB
ONE_MB = 1024 * 1024
SMALL_ENOUGH_THRESHOLD = 250 * ONE_MB
_DEFAULT_BUFFER_SIZE = 1000000


class CsvDataBase:
    """
    Class for encapsulating the data for a single CSV file so that multiple suppliers
    only need one copy of the underlying data
    """

    def __init__(self, has_headers: bool):
        """
        Args:
            has_headers: if there are headers in the CSV files
        """
        self.data = self._load_data()
        if has_headers:
            first_row = self.data.pop(0)
            self.mapping = {first_row[i]: i for i in range(len(first_row))}
        else:
            self.mapping = {}
        self.valid_keys = list(self.mapping.keys())
        if len(self.valid_keys) == 0:
            self.valid_keys = [i + 1 for i in range(len(self.data[0]))]

    def next(self, field: Union[int, str], iteration: int, sample: bool, count: int):
        """
        Obtains the next value(s) for the field for the given iteration

        Args:
            field: key or one based index number
            iteration: current iteration
            sample: if sampling should be used
            count: number of values to return

        Returns:
            array of values if count > 1 else the next value
        """

    def _load_data(self) -> list:
        """
        Method for subclass to load initial data
            the loaded data
        """
        raise NotImplementedError()

    def _get_column_index(self, field: Union[int, str]):
        """
        Resolve the column index

        Args:
            field: key or one based index number

        Returns:
            the column index for the field
        """
        # if we had headers we can use that name, otherwise field should be one based index
        colidx = self.mapping.get(field)
        if colidx is None and not str(field).isdigit():
            raise datagen.SpecException(f'Invalid field name: {field} for csv, known keys: {self.valid_keys}')
        if colidx is None:
            colidx = int(field) - 1
        return colidx


class SampleEnabledCsv(CsvDataBase):
    """
    CSV Data that reads whole file into memory. Supports Sampling of columns and counts greater than 1.
    """

    def __init__(self, csv_path: str, delimiter: str, quotechar: str, has_headers: bool):
        self.csv_path = csv_path
        self.delimiter = delimiter
        self.quotechar = quotechar
        super().__init__(has_headers)

    def _load_data(self):
        with open(self.csv_path, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=self.delimiter, quotechar=self.quotechar)
            return list(reader)

    def next(self, field, iteration, sample, count):
        colidx = self._get_column_index(field)

        values = []
        for i in range(count):
            if sample:
                idx = random.randint(0, len(self.data) - 1)
            else:
                idx = iteration % len(self.data) + i
            values.append(self.data[idx][colidx])
        if count == 1:
            return values[0]
        return values


class BufferedCsvData(CsvDataBase):
    """
    CSV Data that buffers in a section of the CSV file at a time. Does NOT support sampling or counts greater than 1 for
    columns.
    """

    def __init__(self, csv_path: str, delimiter: str, quotechar: str, has_headers: bool, buffer_size: int):
        self.csv_path = csv_path
        self.delimiter = delimiter
        self.quotechar = quotechar
        self.size = buffer_size
        self.increment = -1
        self.data = None  # type: ignore
        self.fill_buffer(0)
        # need to populate data before super constructor call
        super().__init__(has_headers)

    def _load_data(self):
        self.fill_buffer(0)
        return self.data

    def fill_buffer(self, iteration: int):
        """
        Fills the buffer of data for this iteration

        Args:
            iteration: current record number being processed
        """
        new_increment = int(iteration / self.size)
        if new_increment == self.increment:
            return

        self.increment = new_increment
        start = self.size * self.increment + 1
        end = start + self.size + 1
        buff = []
        with open(self.csv_path) as handle:
            rows = csv.reader(handle, delimiter=self.delimiter, quotechar=self.quotechar)
            for line in rows:
                if rows.line_num == end:
                    break
                if rows.line_num >= start:
                    buff.append(line)
        self.data = buff

    def next(self, field, iteration, sample, count):
        if sample:
            raise datagen.SpecException('Large CSV files do not support sample mode')
        if count > 1:
            raise datagen.SpecException('Large CSV files only support count of 1')
        self.fill_buffer(iteration)
        colidx = self._get_column_index(field)

        idx = iteration % self.size
        if idx >= len(self.data):
            raise datagen.SpecException("Exceeded end of CSV data, unable to proceed with large CSV files")
        return self.data[idx][colidx]


class CsvSupplier(datagen.ValueSupplierInterface):
    """
    Class for supplying data from a specific field in a csv file
    """

    def __init__(self, csv_data, field_name, sample, count_supplier: datagen.ValueSupplierInterface):
        self.csv_data = csv_data
        self.field_name = field_name
        self.sample = sample
        self.count_supplier = count_supplier

    def next(self, iteration):
        count = self.count_supplier.next(iteration)
        return self.csv_data.next(self.field_name, iteration, self.sample, count)


# to keep from reloading the same CsvData
_csv_data_cache: Dict[str, CsvDataBase] = {}


@datagen.registry.types('csv')
def _configure_csv(field_spec, loader):
    """ Configures the csv value supplier for this field """
    config = datagen.utils.load_config(field_spec, loader)

    field_name = config.get('column', 1)
    sample = datagen.utils.is_affirmative('sample', config)
    count_supplier = datagen.suppliers.count_supplier_from_data(config.get('count', 1))

    csv_data = _load_csv_data(field_spec, config, loader.datadir)
    return CsvSupplier(csv_data, field_name, sample, count_supplier)


@datagen.registry.schemas('csv')
def _get_csv_schema():
    """ get the schema for the csv type """
    return datagen.schemas.load('csv')


@datagen.registry.types('weighted_csv')
def _configure_weighted_csv(field_spec, loader):
    """ Configures the weighted_csv value supplier for this field """

    config = datagen.utils.load_config(field_spec, loader)

    field_name = config.get('column', 1)
    weight_column = config.get('weight_column', 2)
    count_supplier = datagen.suppliers.count_supplier_from_data(config.get('count', 1))

    datafile = config.get('datafile', datagen.types.get_default('csv_file'))
    csv_path = f'{loader.datadir}/{datafile}'
    has_headers = datagen.utils.is_affirmative('headers', config)
    numeric_index = isinstance(field_name, int)
    if numeric_index and field_name < 1:
        raise datagen.SpecException(f'Invalid index {field_name}, one based indexing used for column numbers')

    if has_headers and not numeric_index:
        choices = _read_named_column(csv_path, field_name)
        weights = _read_named_column_weights(csv_path, weight_column)
    else:
        choices = _read_indexed_column(csv_path, int(field_name), skip_first=numeric_index)
        weights = _read_indexed_column_weights(csv_path, int(weight_column), skip_first=numeric_index)
    return datagen.suppliers.WeightedValueSupplier(choices, weights, count_supplier)


@datagen.registry.schemas('weighted_csv')
def get_weighted_csv_schema():
    """ get the schema for the weighted_csv type """
    return datagen.schemas.load('weighted_csv')


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


ONE_MB = 1024 * 1024


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
    datafile = config.get('datafile', datagen.types.get_default('csv_file'))
    csv_path = f'{datadir}/{datafile}'
    if csv_path in _csv_data_cache:
        return _csv_data_cache.get(csv_path)

    if not os.path.exists(csv_path):
        raise datagen.SpecException(f'Unable to locate data file: {datafile} in data dir: {datadir} for spec: '
                                    + json.dumps(field_spec))
    delimiter = config.get('delimiter', ',')
    # in case tab came in as string
    if delimiter == '\\t':
        delimiter = '\t'
    quotechar = config.get('quotechar', '"')
    has_headers = datagen.utils.is_affirmative('headers', config)

    size_in_bytes = os.stat(csv_path).st_size
    max_csv_size = int(datagen.types.get_default('large_csv_size_mb')) * ONE_MB
    if size_in_bytes <= max_csv_size:
        csv_data = SampleEnabledCsv(csv_path, delimiter, quotechar, has_headers)
    else:
        csv_data = BufferedCsvData(csv_path, delimiter, quotechar, has_headers, _DEFAULT_BUFFER_SIZE)
    _csv_data_cache[csv_path] = csv_data
    return csv_data
