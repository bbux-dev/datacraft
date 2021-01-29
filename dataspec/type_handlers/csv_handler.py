"""
Module for handling csv related data, deals with data typed as 'csv'

"""
import os
import csv
import json
import random
import dataspec
from dataspec import SpecException
from dataspec.utils import is_affirmative
from dataspec.utils import load_config

# 100 MB
SMALL_ENOUGH_THRESHOLD = 100 * 1024 * 1024

# to keep from reloading the same CsvData
_csv_data_cache = {}


class CsvData:
    """
    Class for encapsulating the data for a single CSV file so that multiple suppliers
    only need one copy of the underlying data
    """

    def __init__(self, csv_path, delimiter, quotechar, has_headers):
        with open(csv_path, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=delimiter, quotechar=quotechar)
            self.data = [row for row in reader]
        if has_headers:
            has_headers = self.data.pop(0)
            self.mapping = {has_headers[i]: i for i in range(len(has_headers))}
        else:
            self.mapping = {}
        self.valid_keys = list(self.mapping.keys())
        if len(self.valid_keys) == 0:
            self.valid_keys = [i + 1 for i in range(len(self.data[0]))]

    def next(self, field, iteration, sample, count):
        colidx = self._get_column_index(field)

        values = []
        for i in range(count):
            if sample:
                idx = random.randint(0, len(self.data))
            else:
                idx = iteration % len(self.data) + i
            values.append(self.data[idx][colidx])
        if count == 1:
            return values[0]
        else:
            return values

    def _get_column_index(self, field):
        # if we had headers we can use that name, otherwise field should be one based index
        colidx = self.mapping.get(field)
        if colidx is None and not str(field).isdigit():
            raise SpecException(f'Invalid field name: {field} for csv, known keys: {self.valid_keys}')
        if colidx is None:
            colidx = int(field) - 1
        return colidx


class CsvSupplier:
    def __init__(self, csv_data, field_name, sample, count):
        self.csv_data = csv_data
        self.field_name = field_name
        self.sample = sample
        self.count = count

    def next(self, iteration):
        return self.csv_data.next(self.field_name, iteration, self.sample, self.count)


@dataspec.registry.types('csv')
def configure_csv(field_spec, loader):
    config = load_config(field_spec, loader)

    field_name = config.get('column', 1)
    sample = is_affirmative('sample', config)
    count = int(config.get('count', 1))

    csv_data = _load_csv_data(field_spec, config, loader.datadir)
    return CsvSupplier(csv_data, field_name, sample, count)


def _load_csv_data(field_spec, config, datadir):
    datafile = config.get('datafile', 'data.csv')
    csv_path = f'{datadir}/{datafile}'
    if csv_path in _csv_data_cache:
        return _csv_data_cache.get(csv_path)

    if not os.path.exists(csv_path):
        raise SpecException(f'Unable to locate data file: {datafile} in data dir: {datadir} for spec: '
                            + json.dumps(field_spec))
    size_in_bytes = os.stat(csv_path).st_size
    if size_in_bytes <= SMALL_ENOUGH_THRESHOLD:
        delimiter = config.get('delimiter', ',')
        # in case tab came in as string
        if delimiter == '\\t':
            delimiter = '\t'
        quotechar = config.get('quotechar', '"')
        has_headers = is_affirmative('headers', config)
        csv_data = CsvData(csv_path, delimiter, quotechar, has_headers)
    else:
        raise SpecException(f'Input CSV at {csv_path} too large to use as input!')
    _csv_data_cache[csv_path] = csv_data
    return csv_data
