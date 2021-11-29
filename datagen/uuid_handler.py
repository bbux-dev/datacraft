"""
Module for uuid type
"""

from . import types, utils, schemas
from .exceptions import SpecException
from .supplier.uuid import uuid_supplier

UUID_KEY = 'uuid'


@types.registry.schemas(UUID_KEY)
def _get_uuid_schema():
    """ get the schema for uuid type """
    return schemas.load(UUID_KEY)


@types.registry.types(UUID_KEY)
def _configure_supplier(field_spec, loader):
    """ configure the supplier for uuid types """
    config = utils.load_config(field_spec, loader)
    variant = int(config.get('variant', 4))

    if variant not in [1, 3, 4, 5]:
        raise SpecException('Invalid variant for: ' + field_spec)
    return uuid_supplier(variant)
