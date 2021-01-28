"""
Module for handling csv related data, deals with data typed as 'csv'

"""
import os
import csv
import json
import dataspec
from dataspec import SpecException

# 100 MB
SMALL_ENOUGH_THRESHOLD = 100 * 1024 * 1024

# to keep from reloading the same CsvData
_csv_data_cache = {}


class CsvData:
    def __init__(self, csv_path, delimiter, quotechar, has_headers):
        with open(csv_path, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=delimiter, quotechar=quotechar)
            self.data = [row for row in reader]
        if has_headers:
            headers = self.data.pop(0)
            self.mapping = {headers[i]: i for i in range(len(headers))}
        else:
            self.mapping = {}

    def next(self, field, iteration):
        idx = iteration % len(self.data)
        # if we had headers we can use that name, otherwise field should be one based index
        colidx = self.mapping.get(field)
        if colidx is None and not str(field).isdigit():
            valid_keys = list(self.mapping.keys())
            if len(valid_keys) == 0:
                valid_keys = [i+1 for i in len(self.data[0])]
            raise SpecException(f'Invalid field name: {field} for csv, known keys: {valid_keys}')
        if colidx is None:
            colidx = int(field) - 1

        return self.data[idx][colidx]


class CsvSupplier:
    def __init__(self, csv_data, field_name):
        self.csv_data = csv_data
        self.field_name = field_name

    def next(self, iteration):
        return self.csv_data.next(self.field_name, iteration)


@dataspec.registry.types('csv')
def configure_csv(field_spec, loader):
    config = field_spec.get('config', {})

    field_name = config.get('column', 1)

    csv_data = _load_csv_data(field_spec, loader.datadir)
    return CsvSupplier(csv_data, field_name)


def _load_csv_data(field_spec, datadir):
    config = field_spec.get('config', {})
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
        quotechar = config.get('quotechar', '"')
        has_headers = str(config.get('has_headers', 'False')).lower() in ['yes', 'true', 'on']
        csv_data = CsvData(csv_path, delimiter, quotechar, has_headers)
    else:
        raise SpecException(f'Input CSV at {csv_path} too large to use as input!')
    _csv_data_cache[csv_path] = csv_data
    return csv_data
