"""
Module for unicode_range type
"""
import json

from . import types, utils, suppliers, schemas
from .exceptions import SpecException
from .supplier.unicode import unicode_range_supplier

UNICODE_RANGE_KEY = 'unicode_range'


@types.registry.schemas(UNICODE_RANGE_KEY)
def _get_unicode_range_schema():
    """ get the unicode range schema """
    return schemas.load(UNICODE_RANGE_KEY)


@types.registry.types(UNICODE_RANGE_KEY)
def _configure_supplier(spec, _):
    """ configure the supplier for unicode_range types """
    if 'data' not in spec:
        raise SpecException('data is Required Element for unicode_range specs: ' + json.dumps(spec))
    data = spec['data']
    if not isinstance(data, list):
        raise SpecException(
            f'data should be a list or list of lists with two elements for {UNICODE_RANGE_KEY} specs: ' + json.dumps(spec))
    config = spec.get('config', {})
    if isinstance(data[0], list):
        suppliers_list = [_single_range(sublist, config) for sublist in data]
        return suppliers.from_list_of_suppliers(suppliers_list, True)
    return _single_range(data, config)


def _single_range(data, config):
    """ creates a unicode supplier for a single unicode range """
    # supplies range of data as floats
    range_data = list(range(_decode_num(data[0]), _decode_num(data[1]) + 1))
    # casts the floats to ints
    if utils.any_key_exists(config, ['mean', 'stddev']):
        if 'as_list' not in config:
            config['as_list'] = 'true'
        wrapped = suppliers.list_stat_sampler(range_data, config)
    else:
        wrapped = suppliers.list_count_sampler(range_data, config)
    return unicode_range_supplier(wrapped)


def _decode_num(num):
    """ decodes the num if hex encoded """
    if isinstance(num, str):
        return int(num, 16)
    return int(num)
