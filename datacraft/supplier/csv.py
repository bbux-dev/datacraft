"""
Module for csv supplier implementations
"""
import csv
import random
from abc import ABC, abstractmethod
from typing import Union, Dict

from .exceptions import SupplierException
from .model import ValueSupplierInterface

_DEFAULT_BUFFER_SIZE = 1000000


class CsvData(ABC):
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

    @abstractmethod
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

    @abstractmethod
    def _load_data(self) -> list:
        """
        Method for subclass to load initial data
            the loaded data
        """

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
            raise SupplierException(f'Invalid field name: {field} for csv, known keys: {self.valid_keys}')
        if colidx is None:
            colidx = int(field) - 1
        return colidx


class _SampleEnabledCsv(CsvData):
    """
    CSV Data that reads whole file into memory. Supports Sampling of columns and counts greater than 1.
    """

    def __init__(self, csv_path: str, delimiter: str, quotechar: str, has_headers: bool):
        self.csv_path = csv_path
        self.delimiter = delimiter
        self.quotechar = quotechar
        super().__init__(has_headers)

    def _load_data(self):
        with open(self.csv_path, newline='', encoding='utf-8') as csvfile:
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


class _RowLevelSampleEnabledCsv(CsvData):
    """
    CSV Data that reads whole file into memory. Supports sampling at a row level
    """

    def __init__(self, csv_path: str, delimiter: str, quotechar: str, has_headers: bool):
        self.csv_path = csv_path
        self.delimiter = delimiter
        self.quotechar = quotechar
        self.current = -1
        self.idx = -1
        super().__init__(has_headers)

    def _load_data(self):
        with open(self.csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile, delimiter=self.delimiter, quotechar=self.quotechar)
            return list(reader)

    def next(self, field, iteration, sample, count):
        colidx = self._get_column_index(field)
        # update the index only when the iteration changes
        if iteration != self.current:
            self.current = iteration
            self.idx = random.randint(0, len(self.data) - count)
        values = [self.data[self.idx+i][colidx] for i in range(count)]
        if count == 1:
            return values[0]
        return values


class _BufferedCsvData(CsvData):
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
        with open(self.csv_path, encoding='utf-8') as handle:
            rows = csv.reader(handle, delimiter=self.delimiter, quotechar=self.quotechar)
            for line in rows:
                if rows.line_num == end:
                    break
                if rows.line_num >= start:
                    buff.append(line)
        self.data = buff

    def next(self, field, iteration, sample, count):
        if sample:
            raise SupplierException('Large CSV files do not support sample mode')
        if count > 1:
            raise SupplierException('Large CSV files only support count of 1')
        self.fill_buffer(iteration)
        colidx = self._get_column_index(field)

        idx = iteration % self.size
        if idx >= len(self.data):
            raise SupplierException("Exceeded end of CSV data, unable to proceed with large CSV files")
        return self.data[idx][colidx]


class _CsvSupplier(ValueSupplierInterface):
    """
    Class for supplying data from a specific field in a csv file
    """

    def __init__(self, csv_data, field_name, sample, count_supplier: ValueSupplierInterface):
        self.csv_data = csv_data
        self.field_name = field_name
        self.sample = sample
        self.count_supplier = count_supplier

    def next(self, iteration):
        count = self.count_supplier.next(iteration)
        return self.csv_data.next(self.field_name, iteration, self.sample, count)


# to keep from reloading the same CsvData
_csv_data_cache: Dict[str, CsvData] = {}


def load_csv_data(csv_path: str,
                  delimiter: str,
                  has_headers: bool,
                  quotechar: str,
                  sample_rows: bool,
                  use_buffering: bool) -> CsvData:
    """
    Loads the csv appropriate CSVDataBase

    Args:
        csv_path: Path to CSV file to use
        delimiter: how items are separated
        has_headers: if the CSV file has a header row
        quotechar: what counts as a quote
        sample_rows: if sampling should happen at a row level, not valid if buffering is set to true
        use_buffering: if the source file is large enough that buffering should be employed

    Returns:
        CsvData to supply csv data from
    """
    if csv_path in _csv_data_cache:
        return _csv_data_cache.get(csv_path)  # type: ignore

    if use_buffering:
        if sample_rows:
            csv_data = _RowLevelSampleEnabledCsv(csv_path, delimiter, quotechar, has_headers)  # type: ignore
        else:
            csv_data = _SampleEnabledCsv(csv_path, delimiter, quotechar, has_headers)  # type: ignore
    else:
        csv_data = _BufferedCsvData(csv_path, delimiter, quotechar, has_headers, _DEFAULT_BUFFER_SIZE)  # type: ignore

    _csv_data_cache[csv_path] = csv_data

    return csv_data


def csv_supplier(field_name: str,
                 csv_data: CsvData,
                 count_supplier: ValueSupplierInterface,
                 sample: bool) -> ValueSupplierInterface:
    """
    Creates csv supplier for the given field using the provided csv_data

    Args:
        field_name: name of field to supply data for
        csv_data: csv data to use
        count_supplier: supplier for counts
        sample: if field should be sampled, if supported

    Returns:
        ValueSupplierInterface for csv field
    """
    return _CsvSupplier(csv_data, field_name, sample, count_supplier)
