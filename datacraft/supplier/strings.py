"""Module for string manipulation suppliers"""
from typing import Union

from .model import ValueSupplierInterface


class _CutSupplier(ValueSupplierInterface):
    """cuts portions of output of other suppliers"""
    def __init__(self,
                 wrapped: ValueSupplierInterface,
                 start: int = 0,
                 end: Union[int, None] = None):
        self.wrapped = wrapped
        self.start = start
        self.end = end

    def next(self, iteration):
        value = str(self.wrapped.next(iteration))
        return value[self.start:self.end]


def cut_supplier(supplier: ValueSupplierInterface,
                 start: int = 0,
                 end: Union[int, None] = None):
    return _CutSupplier(supplier, start, end)
