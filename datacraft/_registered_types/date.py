"""module for date type datacraft registry functions"""
import datetime
import json
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
_DATE_EPOCH_KEY = 'date.epoch'
_DATE_EPOCH_MS_KEY = 'date.epoch.ms'
_DATE_EPOCH_MILLIS_KEY = 'date.epoch.millis'
_ISO_FORMAT_NO_MICRO = '%Y-%m-%dT%H:%M:%S'
_ISO_FORMAT_WITH_MICRO = '%Y-%m-%dT%H:%M:%S.%f'


@datacraft.registry.schemas(_DATE_KEY)
@datacraft.registry.schemas(_DATE_ISO_KEY)
@datacraft.registry.schemas(_DATE_ISO_MS_KEY)
@datacraft.registry.schemas(_DATE_ISO_MILLIS_KEY)
@datacraft.registry.schemas(_DATE_ISO_US_KEY)
@datacraft.registry.schemas(_DATE_ISO_MICROS_KEY)
def _get_date_schema():
    """ returns the schema for date types """
    # NOTE: These all share a schema
    return schemas.load(_DATE_KEY)


@datacraft.registry.schemas(_DATE_EPOCH_KEY)
@datacraft.registry.schemas(_DATE_EPOCH_MS_KEY)
@datacraft.registry.schemas(_DATE_EPOCH_MILLIS_KEY)
def _get_date_epoch_schema():
    """ returns the schema for date types """
    # NOTE: These all share a schema
    return schemas.load(_DATE_EPOCH_KEY)


@datacraft.registry.types(_DATE_KEY)
def _configure_date_supplier(field_spec: dict, loader: datacraft.Loader):
    """ configures the date value supplier """
    config = datacraft.utils.load_config(field_spec, loader)
    config['hour_supplier'] = _hour_supplier(config, loader)
    data = field_spec.get('data')
    if data and 'format' in config:
        raise datacraft.SpecException(
            f'Cannot specify both data and format for {_DATE_KEY} type: {json.dumps(field_spec)}')
    if data:
        config['format'] = data
    return datacraft.suppliers.date(**config)


def _hour_supplier(config: dict, loader: datacraft.Loader):
    """ get hour supplier from config if present """
    if 'hours' not in config:
        return None
    return loader.get_from_spec(config['hours'])


@datacraft.registry.types(_DATE_ISO_KEY)
def _configure_supplier_iso(field_spec: dict, loader: datacraft.Loader):
    """ configures the date.iso value supplier """
    return _configure_supplier_custom_date_format(field_spec, loader, _ISO_FORMAT_NO_MICRO)


@datacraft.registry.types(_DATE_ISO_US_KEY)
@datacraft.registry.types(_DATE_ISO_MICROS_KEY)
def _configure_supplier_iso_microseconds(field_spec: dict, loader: datacraft.Loader):
    """ configures the date.iso.us value supplier """
    return _configure_supplier_custom_date_format(field_spec, loader, _ISO_FORMAT_WITH_MICRO)


@datacraft.registry.types(_DATE_ISO_MS_KEY)
@datacraft.registry.types(_DATE_ISO_MILLIS_KEY)
def _configure_supplier_iso_milliseconds(field_spec: dict, loader: datacraft.Loader):
    """ configures the date.iso.ms value supplier """
    micros_supplier = _configure_supplier_custom_date_format(field_spec, loader, _ISO_FORMAT_WITH_MICRO)
    return datacraft.suppliers.cut(micros_supplier, start=0, end=23)


@datacraft.registry.types(_DATE_EPOCH_KEY)
def _configure_date_epoch_supplier(field_spec: dict, _: datacraft.Loader):
    """ configures the date.epoch value supplier """
    config = field_spec.get('config', {})
    return datacraft.suppliers.epoch_date(as_millis=False, **config)


@datacraft.registry.types(_DATE_EPOCH_MS_KEY)
@datacraft.registry.types(_DATE_EPOCH_MILLIS_KEY)
def _configure_date_epoch_millis_supplier(field_spec: dict, _: datacraft.Loader):
    """ configures the date.epoch.ms value supplier """
    config = field_spec.get('config', {})
    return datacraft.suppliers.epoch_date(as_millis=True, **config)


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
    example_four = {"format_as_data:date": "%d-%b-%Y %H:%M"}
    examples = [example_one, example_two, example_tre]
    clis = [common.standard_cli_example_usage(example, 3, pretty=True) for example in examples]
    apis = [common.standard_api_example_usage(example, 3) for example in examples]
    clis.append(common.standard_cli_example_usage(example_four, 3, pretty=True, no_reformat=True))
    apis.append(common.standard_api_example_usage(example_four, 3, no_reformat=True))

    return {
        'cli': '\n'.join(clis),
        'api': '\n'.join(apis)
    }


def register_example_date_usage(key):
    """registers a unique function for the basic usage"""

    @datacraft.registry.usage(key)
    def function():
        suffix = key.replace('date', '')
        example = {
            "timestamp" + suffix: {
                "type": key
            }
        }
        return common.standard_example_usage(example, 3)

    return function


for key in [
    _DATE_ISO_KEY,
    _DATE_ISO_US_KEY,
    _DATE_ISO_MICROS_KEY,
    _DATE_ISO_MS_KEY,
    _DATE_ISO_MILLIS_KEY,
    _DATE_EPOCH_KEY,
    _DATE_EPOCH_MS_KEY,
    _DATE_EPOCH_MILLIS_KEY
]:
    register_example_date_usage(key)


def _configure_supplier_custom_date_format(field_spec, loader, output_date_format):
    """ configures a custom date supplier using the provided date format as the output format """
    config = datacraft.utils.load_config(field_spec, loader)
    # make sure the start and end dates match the ISO format we are using
    start = config.get('start')
    end = config.get('end')
    date_format = config.get('format')
    if start:
        start_date = datetime.datetime.strptime(start, date_format)
        config['start'] = start_date.strftime(output_date_format)
    if end:
        end_date = datetime.datetime.strptime(end, date_format)
        config['end'] = end_date.strftime(output_date_format)
    config['format'] = output_date_format
    # End fixes to support iso
    config['hour_supplier'] = _hour_supplier(config, loader)
    return datacraft.suppliers.date(**config)
