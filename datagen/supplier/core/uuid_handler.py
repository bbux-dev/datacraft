"""
Module for handling uuid types
"""
import uuid

import datagen

UUID_KEY = 'uuid'


class UuidSupplier(datagen.ValueSupplierInterface):
    """ Value Supplier for uuid type """
    def next(self, _):
        return str(uuid.uuid4())


@datagen.registry.schemas(UUID_KEY)
def get_uuid_schema():
    return datagen.schemas.load(UUID_KEY)


@datagen.registry.types(UUID_KEY)
def configure_supplier(_, __):
    """ configure the supplier for uuid types """
    return UuidSupplier()
