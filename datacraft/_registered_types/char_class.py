import json
import logging
import string

import datacraft
from . import schemas

_log = logging.getLogger(__name__)
_CHAR_CLASS_KEY = 'char_class'

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


@datacraft.registry.schemas(_CHAR_CLASS_KEY)
def _get_char_class_schema():
    """ get the schema for the char_class type """
    return schemas.load(_CHAR_CLASS_KEY)


for class_key in _CLASS_MAPPING:
    @datacraft.registry.schemas("cc-" + class_key)
    def _get_char_class_alias_schema():
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


for class_key in _CLASS_MAPPING:
    @datacraft.registry.types("cc-" + class_key)
    def _configure_char_class_alias_supplier(spec, loader):
        """ configure the supplier for char_class alias types """
        spec['data'] = class_key
        return _configure_char_class_supplier(spec, loader)
