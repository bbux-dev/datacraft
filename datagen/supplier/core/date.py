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
import datetime
import json

import datagen
import datagen.model

DATE_KEY = 'date'
DATE_ISO_KEY = 'date.iso'
DATE_ISO_US_KEY = 'date.iso.us'

ISO_FORMAT_NO_MICRO = '%Y-%m-%dT%H:%M:%S'
ISO_FORMAT_WITH_MICRO = '%Y-%m-%dT%H:%M:%S.%f'

SECONDS_IN_DAY = 24.0 * 60.0 * 60.0


@datagen.registry.schemas(DATE_KEY)
def get_date_schema():
    """ returns the schema for date types """
    return datagen.schemas.load(DATE_KEY)


@datagen.registry.schemas(DATE_ISO_KEY)
def get_date_iso_schema():
    """ returns the schema for date.iso types """
    # NOTE: These all share a schema
    return datagen.schemas.load(DATE_KEY)


@datagen.registry.schemas(DATE_ISO_US_KEY)
def get_date_iso_us_schema():
    """ returns the schema for date.iso.us types """
    # NOTE: These all share a schema
    return datagen.schemas.load(DATE_KEY)


class DateSupplier(datagen.ValueSupplierInterface):
    """
    Value Supplier implementation for dates
    """

    def __init__(self,
                 timestamp_distribution: datagen.model.Distribution,
                 date_format_string: str):
        self.date_format = date_format_string
        self.timestamp_distribution = timestamp_distribution

    def next(self, iteration):
        random_seconds = self.timestamp_distribution.next_value()
        next_date = datetime.datetime.fromtimestamp(random_seconds)
        if self.date_format:
            return next_date.strftime(self.date_format)
        return next_date.replace(microsecond=0).isoformat()


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
    return datagen.distributions.uniform(start=start_ts, end=end_ts)


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
    return datagen.distributions.normal(mean=mean, stddev=stddev)


@datagen.registry.types(DATE_KEY)
def configure_supplier(field_spec: dict, loader: datagen.Loader):
    """ configures the date value supplier """
    config = datagen.utils.load_config(field_spec, loader)
    if 'center_date' in config or 'stddev_days' in config:
        return _create_stats_based_date_supplier(config)
    return _create_uniform_date_supplier(config)


def _create_stats_based_date_supplier(config):
    center_date = config.get('center_date')
    stddev_days = config.get('stddev_days', datagen.types.get_default('date_stddev_days'))
    date_format = config.get('format', datagen.types.get_default('date_format'))
    timestamp_distribution = gauss_date_timestamp(center_date, float(stddev_days), date_format)
    return DateSupplier(timestamp_distribution, date_format)


def _create_uniform_date_supplier(config):
    duration_days = config.get('duration_days', 30)
    offset = int(config.get('offset', 0))
    start = config.get('start')
    end = config.get('end')
    date_format = config.get('format', datagen.types.get_default('date_format'))
    timestamp_distribution = uniform_date_timestamp(start, end, offset, duration_days, date_format)
    if timestamp_distribution is None:
        raise datagen.SpecException(f'Unable to generate timestamp supplier from config: {json.dumps(config)}')
    return DateSupplier(timestamp_distribution, date_format)


@datagen.registry.types(DATE_ISO_KEY)
def configure_supplier_iso(field_spec: dict, loader: datagen.Loader):
    """ configures the date.iso value supplier """
    return _configure_supplier_iso_date(field_spec, loader, ISO_FORMAT_NO_MICRO)


@datagen.registry.types(DATE_ISO_US_KEY)
def configure_supplier_iso_microseconds(field_spec: dict, loader: datagen.Loader):
    """ configures the date.iso.us value supplier """
    return _configure_supplier_iso_date(field_spec, loader, ISO_FORMAT_WITH_MICRO)


def _configure_supplier_iso_date(field_spec, loader, iso_date_format):
    """ configures an iso based date supplier using the provided date format """
    config = datagen.utils.load_config(field_spec, loader)

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
