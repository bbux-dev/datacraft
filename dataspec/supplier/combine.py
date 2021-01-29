"""
Module for combine values supplier implementation
"""
from .value_supplier import ValueSupplierInterface


class CombineValuesSupplier(ValueSupplierInterface):
    """
    Class for combining the values from the output of two or more value suppliers
    """

    def __init__(self, suppliers, config=None):
        self.suppliers = suppliers
        self.config = config

    def next(self, iteration):
        values = [str(supplier.next(iteration)) for supplier in self.suppliers]
        if self.config and 'join_with' in self.config:
            joiner = self.config.get('join_with')
        else:
            joiner = ''
        return joiner.join(values)
