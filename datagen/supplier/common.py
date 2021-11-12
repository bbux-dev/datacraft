"""
Module for holding classes for common supporting Value Suppliers.  These are not core suppliers, but are used to
modify or wrap the functionality of the core suppliers.

"""
from typing import List, Union
import random
from collections import deque

import datagen


class SingleValue(datagen.ValueSupplierInterface):
    """
    Encapsulates supplier that only returns a static value
    """

    def __init__(self, data):
        """
        Args:
            data: single value to return every iteration
        """
        self.data = data

    def next(self, _):
        return self.data


class MultipleValueSupplier(datagen.ValueSupplierInterface):
    """
    Supplier that generates list of values based on count parameter
    """

    def __init__(self,
                 wrapped: datagen.ValueSupplierInterface,
                 count_supplier: datagen.ValueSupplierInterface):
        """
        Args:
            wrapped: supplier that provides values
            count_supplier: supplier that provides the number of values to generate
        """
        self.wrapped = wrapped
        self.count_supplier = count_supplier

    def next(self, iteration):
        count = self.count_supplier.next(iteration)
        return [self.wrapped.next(iteration + i) for i in range(count)]


class RotatingSupplierList(datagen.ValueSupplierInterface):
    """
    Class that rotates through a list of suppliers incrementally to provide the next value
    """

    def __init__(self,
                 suppliers: List[datagen.ValueSupplierInterface],
                 modulate_iteration: bool):
        """
        Args:
            suppliers: list of suppliers to rotate through
            modulate_iteration: if the iteration should be split evenly across all suppliers
        """
        self.suppliers = suppliers
        self.modulate_iteration = modulate_iteration

    def next(self, iteration):
        idx = iteration % len(self.suppliers)
        if self.modulate_iteration:
            modulated_iteration = int(iteration / len(self.suppliers))
            return self.suppliers[idx].next(modulated_iteration)
        return self.suppliers[idx].next(iteration)


class DecoratedSupplier(datagen.ValueSupplierInterface):
    """
    Class used to add additional data to other suppliers output, such as a
    prefix or suffix or to surround the output with quotes
    """

    def __init__(self, config: dict, supplier: datagen.ValueSupplierInterface):
        """
        Args:
            config: configuration
            supplier: to decorate
        """
        self.prefix = config.get('prefix', '')
        self.suffix = config.get('suffix', '')
        self.quote = config.get('quote', '')
        self.wrapped = supplier

    def next(self, iteration):
        value = self.wrapped.next(iteration)
        # todo: cache for efficiency?
        return f'{self.quote}{self.prefix}{value}{self.suffix}{self.quote}'


class CastingSupplier(datagen.ValueSupplierInterface):
    """
    Class that just casts the results of other suppliers
    """

    def __init__(self,
                 wrapped: datagen.ValueSupplierInterface,
                 caster: datagen.CasterInterface):
        """
        Args:
            wrapped: supplier to get values from
            caster: to use to cast values
        """
        self.wrapped = wrapped
        self.caster = caster

    def next(self, iteration):
        return self.caster.cast(self.wrapped.next(iteration))


class RandomRangeSupplier(datagen.ValueSupplierInterface):
    """
    Class that supplies values uniformly selected from specified bounds
    """

    def __init__(self,
                 start: Union[str, int, float],
                 end: Union[str, int, float],
                 precision: Union[str, int, float, None],
                 count_supplier: datagen.ValueSupplierInterface):
        """
        Args:
            start: of range
            end: of range
            precision: decimal places to keep
            count_supplier: to supply number of values to return
        """
        self.start = float(start)
        self.end = float(end)
        self.precision = precision
        self.format_str = '{: .' + str(precision) + 'f}'
        self.count_supplier = count_supplier

    def next(self, iteration):
        count = self.count_supplier.next(iteration)
        next_nums = [random.uniform(self.start, self.end) for _ in range(count)]
        if self.precision is not None:
            next_nums = [float(self.format_str.format(next_num)) for next_num in next_nums]
        if count == 1:
            return next_nums[0]
        return next_nums


class DistributionBackedSupplier(datagen.ValueSupplierInterface):
    """
    Class that supplies values selected from a distribution such as a Gaussian or Uniform distribution.

    @see datagen.distributions
    """

    def __init__(self, distribution: datagen.Distribution):
        """
        Args:
            distribution: to use to generate values
        """
        self.distribution = distribution

    def next(self, _):
        return self.distribution.next_value()


class BufferedValueSuppier(datagen.ValueSupplierInterface):
    """
    Class for buffering the values from other suppliers. This allows the interaction
    of one supplier with the previous values of another supplier
    """

    def __init__(self, wrapped: datagen.ValueSupplierInterface, buffer_size: int):
        """
        Args:
            wrapped: supplier to buffer values for
            buffer_size: size of buffer to use
        """
        self.wrapped = wrapped
        self.buffer: deque = deque(maxlen=buffer_size)
        self.current = -1
        self.buffer_size = buffer_size

    def next(self, iteration):
        if iteration > self.current:
            value = self.wrapped.next(iteration)
            self.buffer.append(value)
            self.current = iteration
            return value

        idx = len(self.buffer) - (self.current - iteration) - 1
        if idx < 0:
            raise ValueError('Buffer index out of range')
        return self.buffer[idx]
