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
        if config and 'join_with' in config:
            self.joiner = config.get('join_with')
        else:
            self.joiner = ''

    def next(self, iteration):
        values = [str(supplier.next(iteration)) for supplier in self.suppliers]

        return self.joiner.join(values)
