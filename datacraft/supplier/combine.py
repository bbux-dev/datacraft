"""
Module for combine type implementations
"""
from typing import List

from .model import ValueSupplierInterface


def combine_supplier(suppliers_list: List[ValueSupplierInterface],
                     join_with: str,
                     as_list: bool) -> ValueSupplierInterface:
    """
    Args:
        suppliers_list: list of suppliers to combine in order of combination
        as_list: if the results should be returned as a list
        join_with: value to use to join the values
    """
    return _CombineValuesSupplier(suppliers_list, as_list, join_with)


class _CombineValuesSupplier(ValueSupplierInterface):
    """
    Class for combining the values from the output of two or more value suppliers
    """

    def __init__(self,
                 suppliers_list: List[ValueSupplierInterface],
                 as_list: bool,
                 join_with: str):
        """
        Args:
            suppliers_list: list of suppliers to combine in order of combination
            as_list: if the results should be returned as a list
            join_with: value to use to join the values
        """
        self.suppliers = suppliers_list
        self.as_list = as_list
        self.joiner = join_with

    def next(self, iteration):
        values = [supplier.next(iteration) for supplier in self.suppliers]
        if self.as_list:
            return values
        return self.joiner.join([str(val) for val in values])
