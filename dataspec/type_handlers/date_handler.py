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
import random
import datetime
from dataspec import registry, suppliers, Loader, ValueSupplierInterface
from dataspec.utils import load_config
import dataspec.schemas as schemas

DATE_KEY = 'date'
DATE_ISO_KEY = 'date.iso'
DATE_ISO_US_KEY = 'date.iso.us'
DATE_RANGE_KEY = 'date_range'

DEFAULT_FORMAT = "%d-%m-%Y"
ISO_FORMAT_NO_MICRO = '%Y-%m-%dT%H:%M:%S'
ISO_FORMAT_WITH_MICRO = '%Y-%m-%dT%H:%M:%S.%f'


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

    def __init__(self, delta_days, offset, anchor, date_format_string):
        self.date_format = date_format_string

        offset_date = datetime.timedelta(days=offset)
        if anchor:
            base = datetime.datetime.strptime(anchor, date_format_string) - offset_date
        else:
            base = datetime.datetime.now() - offset_date

        self.start_date, end_date = _calculate_start_end_dates(base, delta_days)
        self.delta_seconds = _calculate_delta_seconds(self.start_date, end_date)

    def next(self, _):
        random_second = random.randrange(self.delta_seconds)
        next_date = self.start_date + datetime.timedelta(seconds=random_second)
        if self.date_format:
            return next_date.strftime(self.date_format)
        return next_date.replace(microsecond=0).isoformat()


class DateRangeSupplier(ValueSupplierInterface):
    """
    Value Supplier implementation for date ranges
    """

    def __init__(self,
                 delta_days: int,
                 offset: ValueSupplierInterface,
                 anchor: str,
                 date_format_string: str,
                 days_in_range: ValueSupplierInterface,
                 join_with=None):
        self.date_format = date_format_string
        self.offset = offset

        if anchor:
            self.anchor_date = datetime.datetime.strptime(anchor, date_format_string)
        else:
            self.anchor_date = datetime.datetime.now()

        # self.start_date, end_date = _calculate_start_end_dates(base, delta_days)
        # self.delta_seconds = _calculate_delta_seconds(self.start_date, end_date)
        self.days_in_range = days_in_range
        self.join_with = join_with

    def next(self, iteration):
        offset = self.offset.next(iteration)
        offset_date = datetime.timedelta(days=offset)
        delta_days = self.days_in_range.next(iteration)
        base = self.anchor_date - offset_date
        start_date, end_date = _calculate_start_end_dates(base, delta_days)
        # random_second = random.randrange(self.delta_seconds)
        # random_day = random.randrange(self.days_in_range)
        # start_date = self.start_date + datetime.timedelta(seconds=random_second)
        # end_date = start_date + datetime.timedelta(days=random_day)
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
    delta_days = config.get('delta_days', 15)
    offset = int(config.get('offset', 0))
    anchor = config.get('anchor')
    date_format = config.get('format', DEFAULT_FORMAT)
    return DateSupplier(delta_days, offset, anchor, date_format)


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
    delta_days = config.get('delta_days', 15)
    offset = get_param(config, ['offset', 'rand_offset'], default=0)
    print(offset)
    offset_supplier = get_value_supplier_for_param(offset)
    print(type(offset_supplier))
    anchor = config.get('anchor')
    date_format = config.get('format', DEFAULT_FORMAT)
    duration_days = get_param(config, ['duration_days', 'rand_duration_days'], default=30)
    duration_days_supplier = get_value_supplier_for_param(duration_days)
    join_with = config.get('join_with')
    return DateRangeSupplier(delta_days, offset_supplier, anchor, date_format, duration_days_supplier, join_with)


def get_param(config: dict, names: List, default):
    for name in names:
        if name in config:
            return config.get(names)
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
    else:
        return suppliers.values(value)


def _configure_supplier_iso_date(field_spec, loader, iso_date_format):
    """ configures an iso based date supplier using the provided date format """
    config = load_config(field_spec, loader)
    delta_days = config.get('delta_days', 15)
    offset = int(config.get('offset', 0))
    anchor = config.get('anchor')
    date_format = config.get('format', DEFAULT_FORMAT)
    # make sure the anchor matches the ISO format we are using
    if anchor:
        anchor_date = datetime.datetime.strptime(anchor, date_format)
        anchor = anchor_date.strftime(iso_date_format)
    return DateSupplier(delta_days, offset, anchor, iso_date_format)


def _calculate_start_end_dates(base, delta_days):
    """
    Calculates the datetime objects for the start of delta_days ago and the start of delta_days+1 ahead
    To guarantee that the desired date range strings are created
    :param base:
    :param delta_days:
    :return:
    """
    lower, upper = _calculate_upper_lower(delta_days)
    start_date = (base + datetime.timedelta(days=lower)).replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = (base + datetime.timedelta(days=upper)).replace(hour=0, minute=0, second=0, microsecond=0)
    return start_date, end_date


def _calculate_upper_lower(delta_days):
    """
    Calculates the lower and upper bounds based on the many formats accepted by delta days
    :param delta_days:
    :return: the lower and upper number of days for delta
    """
    if isinstance(delta_days, list):
        lower = int(delta_days[0])
        upper = int(delta_days[1])
    else:
        lower = -int(delta_days)
        upper = int(delta_days)
    lower = -(abs(lower))
    # this makes end date inclusive
    upper = abs(upper) + 1
    return lower, upper


def _calculate_delta_seconds(start, end):
    """ calculates the delta in seconds between the two dates """
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    return int_delta
