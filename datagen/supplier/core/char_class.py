"""
A ``char_class`` type is used to create strings that are made up of characters
from specific character classes. The strings can be of fixed or variable length.
There are several built in character classes. You can also provide your own set
of characters to sample from. Below is the list of supported character classes:

Built In Classes
----------------

.. list-table::
   :header-rows: 1

   * - class
     - description
   * - ascii
     - All valid ascii characters including control
   * - lower
     - ascii lowercase
   * - upper
     - ascii uppercase
   * - digits
     - Numbers 0 through 9
   * - letters
     - lowercase and uppercase
   * - word
     - letters + digits + '_'
   * - printable
     - All printable ascii chars including whitespace
   * - visible
     - All printable ascii chars excluding whitespace
   * - punctuation
     - local specific punctuation
   * - special
     - local specific punctuation
   * - hex
     - Hexadecimal digits including upper and lower case a-f
   * - hex-lower
     - Hexadecimal digits only including lower case a-f
   * - hex-upper
     - Hexadecimal digits only including upper case A-F

Prototype:

.. code-block:: python

    {
      "<field name>": {
        "type": "char_class":
        or
        "type": "cc-<char_class_name>",
        "data": <char_class_name>,
        or
        "data": <string with custom set of characters to sample from>
        or
        "data": [<char_class_name1>, <char_class_name2>, ..., <custom characters>]
        "config":{
          "exclude": <string of characters to exclude from output>,
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
      "password": {
        "type": "char_class",
        "data": ["word", "special", "hex-lower", "M4$p3c!@l$@uc3"],
        "config": {
          "mean": 14,
          "stddev": 2,
          "min": 10,
          "max": 18,
          "exclude": ["-", "\\""]
        }
      }
    }

.. code-block:: json

    {
      "one_to_five_digits:cc-digits?min=1&max=5": {}
    }

"""
import json
import string

import datagen

CHAR_CLASS_KEY = 'char_class'
_UNDER_SCORE = '_'

_CLASS_MAPPING = {
    "ascii": ''.join(chr(x) for x in range(128)),
    "lower": string.ascii_lowercase,
    "upper": string.ascii_uppercase,
    "letters": string.ascii_letters,
    "word": f'{string.ascii_letters}{string.digits}{_UNDER_SCORE}',
    "printable": string.printable,
    "visible": ''.join(string.printable.split()),
    "punctuation": string.punctuation,
    "special": string.punctuation,
    "digits": string.digits,
    "hex": string.hexdigits,
    "hex-lower": string.digits + 'abcdef',
    "hex-upper": string.digits + 'ABCDEF',
}


@datagen.registry.schemas(CHAR_CLASS_KEY)
def _get_char_class_schema():
    """ get the schema for the char_class type """
    return datagen.schemas.load(CHAR_CLASS_KEY)


for key in _CLASS_MAPPING.keys():
    @datagen.registry.schemas("cc-" + key)
    def _get_char_class_alias_schema():
        """ get the schema for the char_class type """
        return datagen.schemas.load(CHAR_CLASS_KEY)


@datagen.registry.types(CHAR_CLASS_KEY)
def _configure_supplier(spec, _):
    """ configure the supplier for char_class types """
    if 'data' not in spec:
        raise datagen.SpecException(f'Data is required field for char_class type: {json.dumps(spec)}')
    config = spec.get('config', {})
    data = spec['data']
    if isinstance(data, str) and data in _CLASS_MAPPING:
        data = _CLASS_MAPPING[data]
    if isinstance(data, list):
        new_data = [_CLASS_MAPPING[datum] if datum in _CLASS_MAPPING else datum for datum in data]
        data = ''.join(new_data)
    if 'exclude' in config:
        for char_to_exclude in config.get('exclude'):
            data = data.replace(char_to_exclude, '')
    if 'join_with' not in config:
        config['join_with'] = datagen.types.get_default('char_class_join_with')
    if datagen.utils.any_key_exists(config, ['mean', 'stddev']):
        return datagen.suppliers.list_stat_sampler(data, config)
    return datagen.suppliers.list_count_sampler(data, config)


@datagen.registry.types('cc-ascii')
def _configure_ascii_supplier(spec, loader):
    """ configure the supplier for char_class types """
    spec['data'] = 'ascii'
    return _configure_supplier(spec, loader)


@datagen.registry.types('cc-lower')
def _configure_lower_supplier(spec, loader):
    """ configure the supplier for lower char_class types """
    spec['data'] = 'lower'
    return _configure_supplier(spec, loader)


@datagen.registry.types('cc-upper')
def _configure_upper_supplier(spec, loader):
    """ configure the supplier for upper char_class types """
    spec['data'] = 'upper'
    return _configure_supplier(spec, loader)


@datagen.registry.types('cc-letters')
def _configure_letters_supplier(spec, loader):
    """ configure the supplier for letters char_class types """
    spec['data'] = 'letters'
    return _configure_supplier(spec, loader)


@datagen.registry.types('cc-word')
def _configure_word_supplier(spec, loader):
    """ configure the supplier for char_class types """
    spec['data'] = 'word'
    return _configure_supplier(spec, loader)


@datagen.registry.types('cc-printable')
def _configure_printable_supplier(spec, loader):
    """ configure the supplier for char_class types """
    spec['data'] = 'printable'
    return _configure_supplier(spec, loader)


@datagen.registry.types('cc-visible')
def _configure_visible_supplier(spec, loader):
    """ configure the supplier for visible char_class types """
    spec['data'] = 'visible'
    return _configure_supplier(spec, loader)


@datagen.registry.types('cc-punctuation')
def _configure_punctuation_supplier(spec, loader):
    """ configure the supplier for char_class types """
    spec['data'] = 'punctuation'
    return _configure_supplier(spec, loader)


@datagen.registry.types('cc-special')
def _configure_special_supplier(spec, loader):
    """ configure the supplier for special char_class types """
    spec['data'] = 'special'
    return _configure_supplier(spec, loader)


@datagen.registry.types('cc-digits')
def _configure_digits_supplier(spec, loader):
    """ configure the supplier for digits char_class types """
    spec['data'] = 'digits'
    return _configure_supplier(spec, loader)


@datagen.registry.types('cc-hex')
def _configure_hex_supplier(spec, loader):
    """ configure the supplier for hex char_class types """
    spec['data'] = 'hex'
    return _configure_supplier(spec, loader)


@datagen.registry.types('cc-hex-lower')
def _configure_hex_lower_supplier(spec, loader):
    """ configure the supplier for hex-lower char_class types """
    spec['data'] = 'hex-lower'
    return _configure_supplier(spec, loader)


@datagen.registry.types('cc-hex-upper')
def _configure_hex_upper_supplier(spec, loader):
    """ configure the supplier for hex-upper char_class types """
    spec['data'] = 'hex-upper'
    return _configure_supplier(spec, loader)
