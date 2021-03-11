"""
Module for handling unicode ranges
"""
import json
import dataspec
from dataspec.utils import any_key_exists
from dataspec.suppliers import list_stat_sampler, list_count_sampler, from_list_of_suppliers
from dataspec.supplier.value_supplier import ValueSupplierInterface


class UnicodeRangeSupplier(ValueSupplierInterface):
    """ Value Supplier for unicode_range type """

    def __init__(self, wrapped):
        self.wrapped = wrapped

    def next(self, iteration):
        next_value = self.wrapped.next(iteration)
        as_str = [chr(char_as_int) for char_as_int in next_value]
        return ''.join(as_str)


@dataspec.registry.types('unicode_range')
def configure_supplier(spec, _):
    """ configure the supplier for unicode_range types """
    if 'data' not in spec:
        raise dataspec.SpecException('data is Required Element for unicode_range specs' + json.dumps(spec))
    data = spec['data']
    if not isinstance(data, list):
        raise dataspec.SpecException(
            'data is should be a list or list of lists with two elements for unicode_range specs' + json.dumps(spec))
    config = spec.get('config', {})
    if isinstance(data[0], list):
        suppliers = [_single_range(sublist, config) for sublist in data]
        return from_list_of_suppliers(suppliers, True)
    return _single_range(data, config)


def _single_range(data, config):
    # supplies range of data as floats
    range_data = list(range(_decode_num(data[0]), _decode_num(data[1]) + 1))
    # casts the floats to ints
    if any_key_exists(config, ['mean', 'stddev']):
        if 'as_list' not in config:
            config['as_list'] = 'true'
        wrapped = list_stat_sampler(range_data, config)
    else:
        wrapped = list_count_sampler(range_data, config)
    return UnicodeRangeSupplier(wrapped)


def _decode_num(num):
    if isinstance(num, str):
        return int(num, 16)
    return int(num)