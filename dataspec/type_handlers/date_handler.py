"""
Module for handling date related types

The date Field Spec structure is:

{
  "<field name>": {
    "type": "date",
    OR,
    "type": "date.iso",
    OR,
    "type": "date.iso.us",
    "config": {"...": "..."}
  }
}

"""
from typing import Union, List, Dict
import json
import random
import datetime
from dataspec import registry, suppliers, Loader, ValueSupplierInterface, SpecException
from dataspec.utils import load_config
import dataspec.schemas as schemas

DATE_KEY = 'date'
DATE_ISO_KEY = 'date.iso'
DATE_ISO_US_KEY = 'date.iso.us'
DATE_RANGE_KEY = 'date_range'

DEFAULT_FORMAT = "%d-%m-%Y"
ISO_FORMAT_NO_MICRO = '%Y-%m-%dT%H:%M:%S'
ISO_FORMAT_WITH_MICRO = '%Y-%m-%dT%H:%M:%S.%f'

SECONDS_IN_DAY = 24.0 * 60.0 * 60.0


@registry.schemas(DATE_KEY)
def get_date_schema():
    """ returns the schema for date types """
    return schemas.load(DATE_KEY)


@registry.schemas(DATE_ISO_KEY)
def get_date_iso_schema():
    """ returns the schema for date.iso types """
    # NOTE: These all share a schema
    return schemas.load(DATE_KEY)


@registry.schemas(DATE_ISO_US_KEY)
def get_date_iso_us_schema():
    """ returns the schema for date.iso.us types """
    # NOTE: These all share a schema
    return schemas.load(DATE_KEY)


class DateSupplier(ValueSupplierInterface):
    """
    Value Supplier implementation for dates
    """

    def __init__(self,
                 timestamp_supplier: ValueSupplierInterface,
                 date_format_string: str):
        self.date_format = date_format_string
        self.timestamp_supplier = timestamp_supplier

    def next(self, iteration):
        random_seconds = self.timestamp_supplier.next(iteration)
        next_date = datetime.datetime.fromtimestamp(random_seconds)
        if self.date_format:
            return next_date.strftime(self.date_format)
        return next_date.replace(microsecond=0).isoformat()


class UniformTimestampRange(ValueSupplierInterface):
    def __init__(self, start_ts, end_ts):
        self.start_ts = start_ts
        self.end_ts = end_ts

    def next(self, iteration):
        return random.uniform(self.start_ts, self.end_ts)


class GaussTimestampRange(ValueSupplierInterface):
    def __init__(self, mean, stddev):
        self.mean = mean
        self.stddev = stddev

    def next(self, iteration):
        return random.gauss(self.mean, self.stddev)


def uniform_date_timestamp(
        start: str,
        end: str,
        offset: int,
        duration: int,
        date_format_string: str):
    offset_date = datetime.timedelta(days=offset)
    if start:
        start_date = datetime.datetime.strptime(start, date_format_string) - offset_date
    else:
        start_date = datetime.datetime.now() - offset_date
    if end:
        # buffer end date by one to keep inclusive
        end_date = datetime.datetime.strptime(end, date_format_string) \
                   + datetime.timedelta(days=1) - offset_date
    else:
        # start date already include offset, don't include it here
        end_date = start_date + datetime.timedelta(days=abs(int(duration)), seconds=1)

    start_ts = int(start_date.timestamp())
    end_ts = int(end_date.timestamp())
    if end_ts < start_ts:
        return None
    return UniformTimestampRange(start_ts, end_ts)


def gauss_date_timestamp(
        center_date_str: str,
        stddev_days: float,
        date_format_string: str):
    if center_date_str:
        center_date = datetime.datetime.strptime(center_date_str, date_format_string)
    else:
        center_date = datetime.datetime.now()
    mean = center_date.timestamp()
    stddev = stddev_days * SECONDS_IN_DAY
    return GaussTimestampRange(mean, stddev)


class DateRangeSupplier(ValueSupplierInterface):
    """
    Value Supplier implementation for date ranges
    """

    def __init__(self,
                 offset: ValueSupplierInterface,
                 start: str,
                 date_format_string: str,
                 days_in_range: ValueSupplierInterface,
                 join_with=None):
        self.date_format = date_format_string
        self.offset = offset

        if start:
            self.start_date = datetime.datetime.strptime(start, date_format_string)
        else:
            self.start_date = datetime.datetime.now()

        self.days_in_range = days_in_range
        self.join_with = join_with

    def next(self, iteration):
        offset = self.offset.next(iteration)
        offset_date = datetime.timedelta(days=offset)
        duration_days = self.days_in_range.next(iteration)
        base = self.start_date - offset_date
        start_date, end_date = _calculate_start_end_dates(base, duration_days)
        if self.date_format:
            start_date = start_date.strftime(self.date_format)
            end_date = end_date.strftime(self.date_format)
        else:
            start_date = start_date.replace(microsecond=0).isoformat()
            end_date = end_date.replace(microsecond=0).isoformat()
        if self.join_with:
            return self.join_with.join((start_date, end_date))
        return [start_date, end_date]


@registry.types(DATE_KEY)
def configure_supplier(field_spec: dict, loader: Loader):
    """ configures the date value supplier """
    config = load_config(field_spec, loader)
    if 'center_date' in config or 'stddev_days' in config:
        return _create_stats_based_date_supplier(config)
    return _create_uniform_date_supplier(config)


def _create_stats_based_date_supplier(config):
    center_date = config.get('center_date')
    stddev_days = config.get('stddev_days', 15)
    date_format = config.get('format', DEFAULT_FORMAT)
    timestamp_supplier = gauss_date_timestamp(center_date, stddev_days, date_format)
    return DateSupplier(timestamp_supplier, date_format)


def _create_uniform_date_supplier(config):
    duration_days = config.get('duration_days', 30)
    offset = int(config.get('offset', 0))
    start = config.get('start')
    end = config.get('end')
    date_format = config.get('format', DEFAULT_FORMAT)
    timestamp_supplier = uniform_date_timestamp(start, end, offset, duration_days, date_format)
    if timestamp_supplier is None:
        raise SpecException(f'Unable to generate timestamp supplier from config: {json.dumps(config)}')
    return DateSupplier(timestamp_supplier, date_format)


@registry.types(DATE_ISO_KEY)
def configure_supplier_iso(field_spec: dict, loader: Loader):
    """ configures the date.iso value supplier """
    return _configure_supplier_iso_date(field_spec, loader, ISO_FORMAT_NO_MICRO)


@registry.types(DATE_ISO_US_KEY)
def configure_supplier_iso_microseconds(field_spec: dict, loader: Loader):
    """ configures the date.iso.us value supplier """
    return _configure_supplier_iso_date(field_spec, loader, ISO_FORMAT_WITH_MICRO)


@registry.types(DATE_RANGE_KEY)
def configure_date_range_type(field_spec: dict, loader: Loader):
    """ configures the date range value supplier """
    config = load_config(field_spec, loader)
    offset = get_param(config, ['offset', 'rand_offset'], default=0)
    offset_supplier = get_value_supplier_for_param(offset)
    if offset_supplier is None:
        raise SpecException(f'Invalid offset param: {offset}, from {json.dumps(field_spec)}')
    start = config.get('start')
    date_format = config.get('format', DEFAULT_FORMAT)
    duration_days = get_param(config, ['duration_days', 'rand_duration_days'], default=30)
    duration_days_supplier = get_value_supplier_for_param(duration_days)
    join_with = config.get('join_with')
    return DateRangeSupplier(offset_supplier, start, date_format, duration_days_supplier, join_with)


def get_param(config: dict, names: List, default):
    for name in names:
        if name in config:
            return config.get(name)
    return default


def get_value_supplier_for_param(value: Union[int, List[int], Dict[str, float]]):
    """
    Given the type of the value, will return a value supplier for that type
    If it is a list with two entries, then it will be a random range supplier
    otherwise it will conform to what ever value supplier type it specifies:
    constant, list, weighted
    """
    if isinstance(value, list) and len(value) == 2:
        return suppliers.random_range(value[0], value[1])
    elif isinstance(value, str):
        try:
            return suppliers.single_value(int(value))
        except ValueError:
            return None
    elif isinstance(value, dict):
        return suppliers.cast_supplier(suppliers.values(value), field_spec=None, cast_to='int')
    return suppliers.values(value)


def _configure_supplier_iso_date(field_spec, loader, iso_date_format):
    """ configures an iso based date supplier using the provided date format """
    config = load_config(field_spec, loader)

    # make sure the start and end dates match the ISO format we are using
    start = config.get('start')
    end = config.get('end')
    date_format = config.get('format', DEFAULT_FORMAT)
    if start:
        start_date = datetime.datetime.strptime(start, date_format)
        config['start'] = start_date.strftime(iso_date_format)
    if end:
        end_date = datetime.datetime.strptime(end, date_format)
        config['end'] = end_date.strftime(iso_date_format)
    config['format'] = iso_date_format
    # End fixes to support iso

    if 'center_date' in config or 'stddev_days' in config:
        return _create_stats_based_date_supplier(config)
    return _create_uniform_date_supplier(config)


def _calculate_start_end_dates(base, duration_days):
    """
    Calculates the datetime objects for the start of duration_days ago and the start of duration_days+1 ahead
    To guarantee that the desired date range strings are created
    :param base:
    :param duration_days:
    :return:
    """
    lower, upper = _calculate_upper_lower(duration_days)
    start_date = (base + datetime.timedelta(days=lower)).replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = (base + datetime.timedelta(days=upper)).replace(hour=0, minute=0, second=0, microsecond=0)
    return start_date, end_date


def _calculate_upper_lower(duration_days):
    """
    Calculates the lower and upper bounds based on the many formats accepted by delta days
    :param duration_days:
    :return: the lower and upper number of days for delta
    """
    if isinstance(duration_days, list):
        lower = int(duration_days[0])
        upper = int(duration_days[1])
    else:
        lower = -int(duration_days)
        upper = int(duration_days)
    lower = -(abs(lower))
    # this makes end date inclusive
    upper = abs(upper) + 1
    return lower, upper


def _calculate_delta_seconds(start, end):
    """ calculates the delta in seconds between the two dates """
    delta = end - start
    delta_days = delta.days if delta.days > 0 else 1
    int_delta = (delta_days * 24 * 60 * 60) + delta.seconds
    return int_delta
