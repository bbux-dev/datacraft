""" Implementations for range types """
import math
import decimal
from typing import Union

from .model import ValueSupplierInterface, ResettableIterator


def range_wrapped(range_obj: range) -> ValueSupplierInterface:
    """
    Wraps a range object to return values from

    Args:
        range_obj: i.e. range(1), range(2, 7), range(1000, 10000000, 5000)

    Returns:
        ValueSupplierInterface for range
    """
    return WrappedRangeSupplier(range_obj)


class WrappedRangeSupplier(ValueSupplierInterface):
    """ Wraps a range object """
    def __init__(self, range_obj):
        self.range_obj = range_obj
        self.range_iter = iter(self.range_obj)

    def next(self, iteration):
        try:
            val = next(self.range_iter)
        except StopIteration:
            self.range_iter = iter(self.range_obj)
            val = next(self.range_iter)
        return val


def float_range(start: float,
                stop: float,
                step: float = 1,
                precision: Union[int, None] = None) -> ResettableIterator:
    """
    Fancy foot work to support floating point ranges due to rounding errors with the way floating point numbers are
    stored
    Args:
        start: start of range
        stop: end of range
        step: step for range
        precision: number of decimal places to keep

    Returns:
        ResettableIterator for float range

    """
    return _ResettingFloatRange(start, stop, step, precision)


class _ResettingFloatRange(ResettableIterator):
    """ class for producing floats with specific numbers of decimal places """

    def __init__(self,
                 start: float,
                 stop: float,
                 step: float = 1,
                 precision=None):
        self.start = start
        self.dstop = decimal.Decimal(str(stop))
        self.dstep = decimal.Decimal(str(step))
        self.precision = precision
        self.current = decimal.Decimal(str(start))
        self.quantize = decimal.Decimal(str(1 / math.pow(10, 5)))
        self.reset()

    def reset(self):
        # attempt to defeat some rounding errors prevalent in python
        self.current = decimal.Decimal(str(self.start))
        if self.precision:
            self.quantize = decimal.Decimal(str(1 / math.pow(10, int(self.precision))))
            self.current = self.current.quantize(self.quantize)

    def __next__(self) -> float:  # type: ignore
        if self.current >= self.dstop:
            raise StopIteration()
        result = float(str(self.current))
        self.current = self.current + self.dstep
        if self.precision:
            self.current = self.current.quantize(self.quantize)
        return result

    def __iter__(self) -> ResettableIterator:
        return self
