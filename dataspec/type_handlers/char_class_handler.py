"""
Module for handling character class types
"""
import json
import string
import dataspec
from dataspec.supplier.string_sampler import StringSamplerSupplier
from dataspec.utils import any_key_exists
from dataspec.supplier.list_sampler import ListSampler


def _create_chars_for_ranges(ranges):
    chars_as_str = ''
    for ascii_range in ranges:
        if len(ascii_range) == 1:
            chars_as_str = chars_as_str + chr(ascii_range[0])
        else:
            chars_as_str = chars_as_str + ''.join(chr(x) for x in range(ascii_range[0], ascii_range[1] + 1))
    return chars_as_str


_ZERO_TO_NINE = [48, 57]
_LOWER_CASE = [97, 122]
_UPPER_CASE = [65, 90]
_UNDER_SCORE = [95]

_CLASS_MAPPING = {
    "ascii": ''.join(chr(x) for x in range(128)),
    "word": _create_chars_for_ranges([_ZERO_TO_NINE, _LOWER_CASE, _UPPER_CASE, _UNDER_SCORE]),
    "printable": string.printable,
    "special": "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~",
    "digits": ''.join(chr(x) for x in range(9))
}


@dataspec.registry.types('char_class')
def configure_supplier(spec, _):
    """ configure the supplier for char_class types """
    if 'data' not in spec:
        raise dataspec.SpecException(f'Data is required field for char_class type: {json.dumps(spec)}')
    config = spec.get('config', {})
    data = spec['data']
    if isinstance(data, str) and data in _CLASS_MAPPING:
        data = _CLASS_MAPPING[data]
    if 'exclude' in config:
        for char_to_exclude in config.get('exclude'):
            data = data.replace(char_to_exclude, '')
    if any_key_exists(config, ['mean', 'stddev']):
        if 'join_with' not in config:
            config['join_with'] = ''
        return ListSampler(data, config)
    return StringSamplerSupplier(data, config)
