"""
Module for value list supplier implementation
"""
import random
from dataspec.exceptions import SpecException
from .value_supplier import ValueSupplierInterface


class ListValueSupplier(ValueSupplierInterface):
    """
    Value Supplier implementation for supplying values from lists
    """

    def __init__(self, data, do_sampling=False, count=1):
        self.values = data
        self.do_sampling = do_sampling
        try:
            self.count = int(count)
        except ValueError as value_error:
            raise SpecException(f'Invalid count param: {count}') from value_error

    def next(self, iteration):
        if self.do_sampling:
            values = random.sample(self.values, self.count)
        else:
            values = [self._value(iteration, i) for i in range(self.count)]
        if self.count == 1:
            return values[0]
        return values

    def _value(self, iteration, i):
        idx = (iteration + i) % len(self.values)
        return self.values[idx]
