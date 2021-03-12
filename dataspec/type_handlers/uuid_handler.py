"""
Module for handling uuid types
"""
import uuid
import dataspec
from dataspec.supplier.value_supplier import ValueSupplierInterface
import dataspec.schemas as schemas

UUID_KEY = 'uuid'


class UuidSupplier(ValueSupplierInterface):
    """ Value Supplier for uuid type """
    def next(self, _):
        return str(uuid.uuid4())


@dataspec.registry.schemas(UUID_KEY)
def get_uuid_schema():
    return schemas.load(UUID_KEY)


@dataspec.registry.types(UUID_KEY)
def configure_supplier(_, __):
    """ configure the supplier for uuid types """
    return UuidSupplier()
