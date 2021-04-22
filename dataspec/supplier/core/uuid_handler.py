"""
Module for handling uuid types
"""
import uuid
import dataspec
from .value_supplier import ValueSupplierInterface

UUID_KEY = 'uuid'


class UuidSupplier(ValueSupplierInterface):
    """ Value Supplier for uuid type """
    def next(self, _):
        return str(uuid.uuid4())


@dataspec.registry.schemas(UUID_KEY)
def get_uuid_schema():
    return dataspec.schemas.load(UUID_KEY)


@dataspec.registry.types(UUID_KEY)
def configure_supplier(_, __):
    """ configure the supplier for uuid types """
    return UuidSupplier()
