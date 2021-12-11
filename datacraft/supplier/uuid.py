"""
Module for uuid value supplier implementations
"""
import uuid

from .model import ValueSupplierInterface


def uuid_supplier(variant) -> ValueSupplierInterface:
    """
    Creates a UUid Value Supplier

    Args:
        variant: of uuid to use, default is 4

    Returns:
        ValueSupplierInterface to supply uuids with
    """
    supplier_map = {
        1: _Uuid1(),
        3: _Uuid3(),
        4: _Uuid4(),
        5: _Uuid5(),
    }
    return supplier_map.get(variant)  # type: ignore


class _Uuid1(ValueSupplierInterface):
    """ uuid1 supplier class """
    def next(self, _):
        return str(uuid.uuid1())


class _Uuid3(ValueSupplierInterface):
    """ uuid3 supplier class """
    def __init__(self):
        self.namespace = uuid.uuid4()

    def next(self, iteration):
        return str(uuid.uuid3(self.namespace, str(iteration)))


class _Uuid4(ValueSupplierInterface):
    """ uuid4 supplier class """
    def next(self, iteration):
        return str(uuid.uuid4())


class _Uuid5(ValueSupplierInterface):
    """ uuid5 supplier class """
    def __init__(self):
        self.namespace = uuid.uuid4()

    def next(self, iteration):
        return str(uuid.uuid5(self.namespace, str(iteration)))
