import datetime
import logging

import datacraft
from . import schemas

_log = logging.getLogger(__name__)
_DATE_KEY = 'date'
_DATE_ISO_KEY = 'date.iso'
_DATE_ISO_US_KEY = 'date.iso.us'
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
def _get_date_iso_us_schema():
    """ returns the schema for date.iso.us types """
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
def _configure_supplier_iso_microseconds(field_spec: dict, loader: datacraft.Loader):
    """ configures the date.iso.us value supplier """
    return _configure_supplier_iso_date(field_spec, loader, _ISO_FORMAT_WITH_MICRO)


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
