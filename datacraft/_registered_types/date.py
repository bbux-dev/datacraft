"""module for date type datacraft registry functions"""
import datetime
import logging

import datacraft
from . import common
from . import schemas

_log = logging.getLogger(__name__)
_DATE_KEY = 'date'
_DATE_ISO_KEY = 'date.iso'
_DATE_ISO_MS_KEY = 'date.iso.ms'
_DATE_ISO_MILLIS_KEY = 'date.iso.millis'
_DATE_ISO_US_KEY = 'date.iso.us'
_DATE_ISO_MICROS_KEY = 'date.iso.micros'
_ISO_FORMAT_NO_MICRO = '%Y-%m-%dT%H:%M:%S'
_ISO_FORMAT_WITH_MICRO = '%Y-%m-%dT%H:%M:%S.%f'


@datacraft.registry.schemas(_DATE_KEY)
def _get_date_schema():
    """ returns the schema for date types """
    return schemas.load(_DATE_KEY)


@datacraft.registry.schemas(_DATE_ISO_KEY)
def _get_date_iso_schema():
    """ returns the schema for date.iso types """
    # NOTE: These all share a schema
    return schemas.load(_DATE_KEY)


@datacraft.registry.schemas(_DATE_ISO_US_KEY)
@datacraft.registry.schemas(_DATE_ISO_MICROS_KEY)
def _get_date_iso_us_schema():
    """ returns the schema for date.iso.us types """
    # NOTE: These all share a schema
    return schemas.load(_DATE_KEY)


@datacraft.registry.schemas(_DATE_ISO_MS_KEY)
@datacraft.registry.schemas(_DATE_ISO_MILLIS_KEY)
def _get_date_iso_ms_schema():
    """ returns the schema for date.iso.ms types """
    # NOTE: These all share a schema
    return schemas.load(_DATE_KEY)


@datacraft.registry.types(_DATE_KEY)
def _configure_date_supplier(field_spec: dict, loader: datacraft.Loader):
    """ configures the date value supplier """
    config = datacraft.utils.load_config(field_spec, loader)
    config['hour_supplier'] = _hour_supplier(config, loader)
    return datacraft.suppliers.date(**config)


def _hour_supplier(config: dict, loader: datacraft.Loader):
    """ get hour supplier from config if present """
    if 'hours' not in config:
        return None
    return loader.get_from_spec(config['hours'])


@datacraft.registry.types(_DATE_ISO_KEY)
def _configure_supplier_iso(field_spec: dict, loader: datacraft.Loader):
    """ configures the date.iso value supplier """
    return _configure_supplier_iso_date(field_spec, loader, _ISO_FORMAT_NO_MICRO)


@datacraft.registry.types(_DATE_ISO_US_KEY)
@datacraft.registry.types(_DATE_ISO_MICROS_KEY)
def _configure_supplier_iso_microseconds(field_spec: dict, loader: datacraft.Loader):
    """ configures the date.iso.us value supplier """
    return _configure_supplier_iso_date(field_spec, loader, _ISO_FORMAT_WITH_MICRO)


@datacraft.registry.types(_DATE_ISO_MS_KEY)
@datacraft.registry.types(_DATE_ISO_MILLIS_KEY)
def _configure_supplier_iso_milliseconds(field_spec: dict, loader: datacraft.Loader):
    """ configures the date.iso.ms value supplier """
    micros_supplier = _configure_supplier_iso_date(field_spec, loader, _ISO_FORMAT_WITH_MICRO)
    return datacraft.suppliers.cut(micros_supplier, start=0, end=23)


@datacraft.registry.usage(_DATE_KEY)
def _example_date_usage():
    example_one = {
        "dates": {
            "type": "date",
            "config": {
                "duration_days": "90",
                "start": "15-Dec-2050 12:00",
                "format": "%d-%b-%Y %H:%M"
            }
        }
    }
    example_two = {
        "dates": {
            "type": "date",
            "config": {
                "center_date": "20500601 12:00",
                "format": "%Y%m%d %H:%M",
                "stddev_days": "2"
            }
        }
    }
    example_tre = {
        "start_time": {
            "type": "date",
            "config": {
                "center_date": "20500601 12:00",
                "format": "%Y%m%d %H:%M",
                "hours": {
                    "type": "values",
                    "data": {"7": 0.1, "8": 0.2, "9": 0.4, "10": 0.2, "11": 0.1}
                }
            }
        }
    }
    one = common.standard_example_usage(example_one, 3)
    two = common.standard_example_usage(example_two, 3)
    tre = common.standard_example_usage(example_tre, 3)
    return '\n'.join([one, two, tre])


@datacraft.registry.usage(_DATE_ISO_KEY)
def _example_date_iso_usage():
    example = {
        "timestamp": {
            "type": _DATE_ISO_KEY
        }
    }
    return common.standard_example_usage(example, 3)


@datacraft.registry.usage(_DATE_ISO_US_KEY)
@datacraft.registry.usage(_DATE_ISO_MICROS_KEY)
def _example_date_iso_micros_usage():
    example = {
        "timestamp.us": {
            "type": _DATE_ISO_US_KEY
        }
    }
    return common.standard_example_usage(example, 3)


@datacraft.registry.usage(_DATE_ISO_MS_KEY)
@datacraft.registry.usage(_DATE_ISO_MILLIS_KEY)
def _example_date_iso_millis_usage():
    example = {
        "timestamp.us": {
            "type": _DATE_ISO_US_KEY
        }
    }
    return common.standard_example_usage(example, 3)


def _configure_supplier_iso_date(field_spec, loader, iso_date_format):
    """ configures an iso based date supplier using the provided date format """
    config = datacraft.utils.load_config(field_spec, loader)
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
    config['hour_supplier'] = _hour_supplier(config, loader)
    return datacraft.suppliers.date(**config)
