"""
Generates strings from unicode ranges

Prototype:

.. code-block:: python

    {
      "<field>": {
        "type": "unicode_range":
        "data": [<start_code_point_in_hex>, <end_code_point_in_hex>],
        or
        "data": [
            [<start_code_point_in_hex>, <end_code_point_in_hex>],
            [<start_code_point_in_hex>, <end_code_point_in_hex>],
            ...
            [<start_code_point_in_hex>, <end_code_point_in_hex>],
        ],
        "config":{
          # String Size Based Config Parameters
          "min": <min number of characters in string>,
          "max": <max number of characters in string>,
          or
          "count": <exact number of characters in string>
          or
          "mean": <mean number of characters in string>
          "stddev": <standard deviation from mean for number of characters in string>
          "min": <optional min>
          "max": <optional max>
        }
      }
    }

Examples:

.. code-block:: json

    {
      "text": {
        "type": "unicode_range",
        "data": ["3040", "309f"],
        "config": {
          "mean": 5
        }
      }
    }

"""
import json

import datagen

UNICODE_RANGE_KEY = 'unicode_range'


class UnicodeRangeSupplier(datagen.ValueSupplierInterface):
    """ Value Supplier for unicode_range type """

    def __init__(self, wrapped: datagen.ValueSupplierInterface):
        """
        Args:
            wrapped: supplier that supplies unicode code points
        """
        self.wrapped = wrapped

    def next(self, iteration):
        next_value = self.wrapped.next(iteration)
        as_str = [chr(char_as_int) for char_as_int in next_value]
        return ''.join(as_str)


@datagen.registry.schemas(UNICODE_RANGE_KEY)
def _get_unicode_range_schema():
    """ get the unicode range schema """
    return datagen.schemas.load(UNICODE_RANGE_KEY)


@datagen.registry.types(UNICODE_RANGE_KEY)
def _configure_supplier(spec, _):
    """ configure the supplier for unicode_range types """
    if 'data' not in spec:
        raise datagen.SpecException('data is Required Element for unicode_range specs: ' + json.dumps(spec))
    data = spec['data']
    if not isinstance(data, list):
        raise datagen.SpecException(
            f'data should be a list or list of lists with two elements for {UNICODE_RANGE_KEY} specs: ' + json.dumps(spec))
    config = spec.get('config', {})
    if isinstance(data[0], list):
        suppliers = [_single_range(sublist, config) for sublist in data]
        return datagen.suppliers.from_list_of_suppliers(suppliers, True)
    return _single_range(data, config)


def _single_range(data, config):
    """ creates a unicode supplier for a single unicode range """
    # supplies range of data as floats
    range_data = list(range(_decode_num(data[0]), _decode_num(data[1]) + 1))
    # casts the floats to ints
    if datagen.utils.any_key_exists(config, ['mean', 'stddev']):
        if 'as_list' not in config:
            config['as_list'] = 'true'
        wrapped = datagen.suppliers.list_stat_sampler(range_data, config)
    else:
        wrapped = datagen.suppliers.list_count_sampler(range_data, config)
    return UnicodeRangeSupplier(wrapped)


def _decode_num(num):
    """ decodes the num if hex encoded """
    if isinstance(num, str):
        return int(num, 16)
    return int(num)
