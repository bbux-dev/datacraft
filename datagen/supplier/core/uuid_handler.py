"""
Module for uuid type
"""
import uuid

import datagen

UUID_KEY = 'uuid'


class UuidSupplier(datagen.ValueSupplierInterface):
    """ Value Supplier for uuid type """
    def __init__(self, func):
        self.func = func

    def next(self, _):
        return str(uuid.uuid4())


@datagen.registry.schemas(UUID_KEY)
def _get_uuid_schema():
    """ get the schema for uuid type """
    return datagen.schemas.load(UUID_KEY)


@datagen.registry.types(UUID_KEY)
def _configure_supplier(field_spec, loader):
    """ configure the supplier for uuid types """
    config = datagen.utils.load_config(field_spec, loader)
    variant = int(config.get('variant', 4))
    _func_map = {
        1: uuid.uuid1,
        3: uuid.uuid3,
        4: uuid.uuid4,
        5: uuid.uuid5
    }
    if variant not in _func_map:
        raise datagen.SpecException('Invalid variant for: ' + field_spec)
    return UuidSupplier(_func_map.get(variant))
