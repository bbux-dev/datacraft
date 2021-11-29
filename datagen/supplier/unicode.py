"""
Module for unicode value supplier implementations
"""
from .model import ValueSupplierInterface


def unicode_range_supplier(wrapped: ValueSupplierInterface):
    """
    Args:
        wrapped: supplier that supplies unicode code points
    """
    return _UnicodeRangeSupplier(wrapped)


class _UnicodeRangeSupplier(ValueSupplierInterface):
    """ Value Supplier for unicode_range type """

    def __init__(self, wrapped: ValueSupplierInterface):
        """
        Args:
            wrapped: supplier that supplies unicode code points
        """
        self.wrapped = wrapped

    def next(self, iteration):
        next_value = self.wrapped.next(iteration)
        as_str = [chr(char_as_int) for char_as_int in next_value]
        return ''.join(as_str)
