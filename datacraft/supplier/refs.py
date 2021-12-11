"""
Module for ref related value supplier implementations
"""

from typing import Dict

from .model import ValueSupplierInterface
from .exceptions import SupplierException


def weighted_ref_supplier(key_supplier: ValueSupplierInterface,
                          values_map: Dict[str, ValueSupplierInterface]) -> ValueSupplierInterface:
    """
    Args:
        key_supplier: supplier for ref keys
        values_map: mapping of ref name to supplier for ref
    """
    return _WeightedRefsSupplier(key_supplier, values_map)


class _WeightedRefsSupplier(ValueSupplierInterface):
    """
    Value supplier that uses a weighted scheme to supply values from different reference value suppliers
    """

    def __init__(self,
                 key_supplier: ValueSupplierInterface,
                 values_map: Dict[str, ValueSupplierInterface]):
        """
        Args:
            key_supplier: supplier for ref keys
            values_map: mapping of ref name to supplier for ref
        """
        self.key_supplier = key_supplier
        self.values_map = values_map

    def next(self, iteration):
        key = self.key_supplier.next(iteration)
        supplier = self.values_map.get(key)
        if supplier is None:
            raise SupplierException("Unknown Key '%s' for Weighted Reference" % key)
        return supplier.next(iteration)
