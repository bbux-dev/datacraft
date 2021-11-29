"""
Module for date types: date, date.iso, date.iso.us
"""
import datetime
import json
import logging
from typing import Union

from . import types, schemas, distributions
from .exceptions import SpecException
from .loader import Loader
from .supplier.date import date_supplier
from .supplier.model import Distribution
from . import utils

_DATE_KEY = 'date'
_DATE__ISO_KEY = 'date.iso'
_DATE__ISO_US_KEY = 'date.iso.us'

_ISO_FORMAT_NO_MICRO = '%Y-%m-%dT%H:%M:%S'
_ISO_FORMAT_WITH_MICRO = '%Y-%m-%dT%H:%M:%S.%f'

_SECONDS_IN_DAY = 24.0 * 60.0 * 60.0

_log = logging.getLogger(__name__)


@types.registry.schemas(_DATE_KEY)
def _get_date_schema():
    """ returns the schema for date types """
    return schemas.load(_DATE_KEY)


@types.registry.schemas(_DATE__ISO_KEY)
def _get_date_iso_schema():
    """ returns the schema for date.iso types """
    # NOTE: These all share a schema
    return schemas.load(_DATE_KEY)


@types.registry.schemas(_DATE__ISO_US_KEY)
def _get_date_iso_us_schema():
    """ returns the schema for date.iso.us types """
    # NOTE: These all share a schema
    return schemas.load(_DATE_KEY)


def _uniform_date_timestamp(
        start: str,
        end: str,
        offset: int,
        duration: int,
        date_format_string: str) -> Union[None, Distribution]:
    """
    Creates a uniform distribution for the start and end dates shifted by the offset

    Args:
        start: start date string
        end: end date string
        offset: number of days to shift the duration, positive is back negative is forward
        duration: number of days after start
        date_format_string: format for parsing dates

    Returns:
        Distribution that gives uniform seconds since epoch for the given params
    """
    offset_date = datetime.timedelta(days=offset)
    if start:
        try:
            start_date = datetime.datetime.strptime(start, date_format_string) - offset_date
        except TypeError as err:
            raise SpecException(f"TypeError. Format: {date_format_string}, may not match param: {start}") from err
    else:
        start_date = datetime.datetime.now() - offset_date
    if end:
        # buffer end date by one to keep inclusive
        try:
            end_date = datetime.datetime.strptime(end, date_format_string) \
                + datetime.timedelta(days=1) - offset_date
        except TypeError as err:
            raise SpecException(f"TypeError. Format: {date_format_string}, may not match param: {end}") from err
    else:
        # start date already include offset, don't include it here
        end_date = start_date + datetime.timedelta(days=abs(int(duration)), seconds=1)

    start_ts = int(start_date.timestamp())
    end_ts = int(end_date.timestamp())
    if end_ts < start_ts:
        _log.warning("End date (%s) is before start date (%s)", start_date, end_date)
        return None
    return distributions.uniform(start=start_ts, end=end_ts)


def _gauss_date_timestamp(
        center_date_str: Union[str, None],
        stddev_days: float,
        date_format_string: str):
    """
    Creates a normally distributed date distribution around the center date

    Args:
        center_date_str: center date for distribution
        stddev_days: standard deviation from center date in days
        date_format_string: format for returned dates

    Returns:
        Distribution that gives normally distributed seconds since epoch for the given params
    """
    if center_date_str:
        center_date = datetime.datetime.strptime(center_date_str, date_format_string)
    else:
        center_date = datetime.datetime.now()
    mean = center_date.timestamp()
    stddev = stddev_days * _SECONDS_IN_DAY
    return distributions.normal(mean=mean, stddev=stddev)


@types.registry.types(_DATE_KEY)
def _configure_supplier(field_spec: dict, loader: Loader):
    """ configures the date value supplier """
    config = utils.load_config(field_spec, loader)
    if 'center_date' in config or 'stddev_days' in config:
        return _create_stats_based_date_supplier(config)
    return _create_uniform_date_supplier(config)


def _create_stats_based_date_supplier(config: dict):
    """ creates stats based date supplier from config """
    center_date = config.get('center_date')
    stddev_days = config.get('stddev_days', types.get_default('date_stddev_days'))
    date_format = config.get('format', types.get_default('date_format'))
    timestamp_distribution = _gauss_date_timestamp(center_date, float(stddev_days), date_format)
    return date_supplier(date_format, timestamp_distribution)


def _create_uniform_date_supplier(config):
    """ creates uniform based date supplier from config """
    duration_days = config.get('duration_days', 30)
    offset = int(config.get('offset', 0))
    start = config.get('start')
    end = config.get('end')
    date_format = config.get('format', types.get_default('date_format'))
    timestamp_distribution = _uniform_date_timestamp(start, end, offset, duration_days, date_format)
    if timestamp_distribution is None:
        raise SpecException(f'Unable to generate timestamp supplier from config: {json.dumps(config)}')
    return date_supplier(date_format, timestamp_distribution)


@types.registry.types(_DATE__ISO_KEY)
def _configure_supplier_iso(field_spec: dict, loader: Loader):
    """ configures the date.iso value supplier """
    return _configure_supplier_iso_date(field_spec, loader, _ISO_FORMAT_NO_MICRO)


@types.registry.types(_DATE__ISO_US_KEY)
def _configure_supplier_iso_microseconds(field_spec: dict, loader: Loader):
    """ configures the date.iso.us value supplier """
    return _configure_supplier_iso_date(field_spec, loader, _ISO_FORMAT_WITH_MICRO)


def _configure_supplier_iso_date(field_spec, loader, iso_date_format):
    """ configures an iso based date supplier using the provided date format """
    config = utils.load_config(field_spec, loader)

    # make sure the start and end dates match the ISO format we are using
    start = config.get('start')
    end = config.get('end')
    date_format = config.get('format', )
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
