"""
Module for handling uuid types
"""
import uuid
import dataspec
from dataspec.supplier.value_supplier import ValueSupplierInterface


class UuidSupplier(ValueSupplierInterface):
    """ Value Supplier for uuid type """
    def next(self, _):
        return str(uuid.uuid4())


@dataspec.registry.types('uuid')
def configure_supplier(_, __):
    """ configure the supplier for uuid types """
    return UuidSupplier()
