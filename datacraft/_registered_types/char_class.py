"""module for char_class type datacraft registry functions"""
import json
import logging
import string

import datacraft
from . import common
from . import schemas

_log = logging.getLogger(__name__)
_CHAR_CLASS_KEY = 'char_class'

_UNDER_SCORE = '_'

_CLASS_MAPPING = {
    "ascii": string.printable,
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

_EXAMPLE_SPEC = {
    "password": {
        "type": "char_class",
        "data": ["word", "special", "hex-lower", "M4$p3c!@l$@uc3"],
        "config": {
            "mean": 14,
            "stddev": 2,
            "min": 10,
            "max": 18,
            "exclude": ["-", "\""]
        }
    }
}


@datacraft.registry.schemas(_CHAR_CLASS_KEY)
def _get_char_class_schema():
    """ get the schema for the char_class type """
    return schemas.load(_CHAR_CLASS_KEY)


@datacraft.registry.types(_CHAR_CLASS_KEY)
def _configure_char_class_supplier(spec, loader):
    """ configure the supplier for char_class types """
    if 'data' not in spec:
        raise datacraft.SpecException(f'Data is required field for char_class type: {json.dumps(spec)}')
    config = datacraft.utils.load_config(spec, loader)
    data = spec['data']
    if isinstance(data, str) and data in _CLASS_MAPPING:
        data = _CLASS_MAPPING[data]
    if isinstance(data, list):
        new_data = [_CLASS_MAPPING[datum] if datum in _CLASS_MAPPING else datum for datum in data]
        data = ''.join(new_data)

    if 'join_with' not in config:
        config['join_with'] = datacraft.registries.get_default('char_class_join_with')

    return datacraft.suppliers.character_class(data, **config)


def register_alias_type_function(key, name):
    """registers and alias function for the given char_class key"""
    @datacraft.registry.types(key)
    def function(spec, loader):
        """ configure the supplier for char_class alias types """
        spec['data'] = name
        return _configure_char_class_supplier(spec, loader)

    return function


def register_alias_type_schema(key):
    """registers a schema function for the given char_class key"""
    @datacraft.registry.schemas(key)
    def function():
        """ configure the schema for char_class alias types """
        # start with character class schema
        schema = schemas.load(_CHAR_CLASS_KEY)
        # "properties": {
        #     "type": {"type": "string", "pattern": "^char_class$"}, <- replace this
        schema['properties']['type']['pattern'] = f'^{key}$'
        # drop requirement for data, since this is injected by the cc-<name>
        schema['required'] = ['type']
        return schema

    return function


@datacraft.registry.usage(_CHAR_CLASS_KEY)
def _char_class_usage():
    """basic usage example for char class"""
    return common.standard_example_usage(_EXAMPLE_SPEC, 3)


def register_alias_usage_function(key):
    """registers usage information for the given char_class alias key"""
    @datacraft.registry.usage(key)
    def function():
        """basic usage example for char class"""
        spec = {
            "example": {
                "type": key,
                "config": {"count": 5}
            }
        }
        return common.standard_example_usage(spec, 3)

    return function


for class_name in _CLASS_MAPPING:
    class_key = "cc-" + class_name
    register_alias_type_function(class_key, class_name)
    register_alias_type_schema(class_key)
    register_alias_usage_function(class_key)
