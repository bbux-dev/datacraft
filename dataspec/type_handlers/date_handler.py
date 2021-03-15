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
import random
import datetime
from dataspec import registry, ValueSupplierInterface
from dataspec.utils import load_config
import dataspec.schemas as schemas

DATE_KEY = 'date'
DATE_ISO_KEY = 'date.iso'
DATE_ISO_US_KEY = 'date.iso.us'

DEFAULT_FORMAT = "%d-%m-%Y"
ISO_FORMAT_NO_MICRO = '%Y-%m-%dT%H:%M:%S'
ISO_FORMAT_WITH_MICRO = '%Y-%m-%dT%H:%M:%S.%f'


@registry.schemas(DATE_KEY)
def get_date_schema():
    return schemas.load(DATE_KEY)


@registry.schemas(DATE_ISO_KEY)
def get_date_iso_schema():
    # NOTE: These all share a schema
    return schemas.load(DATE_KEY)


@registry.schemas(DATE_ISO_US_KEY)
def get_date_iso_us_schema():
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


@registry.types(DATE_KEY)
def configure_supplier(field_spec, loader):
    """ configures the date value supplier """
    config = load_config(field_spec, loader)
    delta_days = config.get('delta_days', 15)
    offset = int(config.get('offset', 0))
    anchor = config.get('anchor')
    date_format = config.get('format', DEFAULT_FORMAT)
    return DateSupplier(delta_days, offset, anchor, date_format)


@registry.types(DATE_ISO_KEY)
def configure_supplier_iso(field_spec, loader):
    """ configures the date.iso value supplier """
    return _configure_supplier_iso_date(field_spec, loader, ISO_FORMAT_NO_MICRO)


@registry.types(DATE_ISO_US_KEY)
def configure_supplier_iso_microseconds(field_spec, loader):
    """ configures the date.iso.us value supplier """
    return _configure_supplier_iso_date(field_spec, loader, ISO_FORMAT_WITH_MICRO)


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
