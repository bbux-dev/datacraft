"""
Module for holding classes for common supporting Value Suppliers.  These are not core suppliers, but are used to
modify or wrap the functionality of the core suppliers.

"""
import math
from typing import List, Union, Optional
import random
from collections import deque

from .model import ValueSupplierInterface, CasterInterface, Distribution, ResettableIterator


class SingleValue(ValueSupplierInterface):
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


class MultipleValueSupplier(ValueSupplierInterface):
    """
    Supplier that generates list of values based on count parameter
    """

    def __init__(self,
                 wrapped: ValueSupplierInterface,
                 count_supplier: ValueSupplierInterface):
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


class RotatingSupplierList(ValueSupplierInterface):
    """
    Class that rotates through a list of suppliers incrementally to provide the next value
    """

    def __init__(self,
                 suppliers: List[ValueSupplierInterface],
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


class DecoratedSupplier(ValueSupplierInterface):
    """
    Class used to add additional data to other suppliers output, such as a
    prefix or suffix or to surround the output with quotes
    """

    def __init__(self, supplier: ValueSupplierInterface, **kwargs):
        """
        Args:
            supplier: to alter
            **kwargs
        """
        self.prefix = kwargs.get('prefix', '')
        self.suffix = kwargs.get('suffix', '')
        self.quote = kwargs.get('quote', '')
        self.wrapped = supplier

    def next(self, iteration):
        value = self.wrapped.next(iteration)
        if isinstance(value, list):
            return [self._format(val) for val in value]
        # todo: cache for efficiency?
        return self._format(value)

    def _format(self, value):
        return f'{self.quote}{self.prefix}{value}{self.suffix}{self.quote}'


class CastingSupplier(ValueSupplierInterface):
    """
    Class that just casts the results of other suppliers
    """

    def __init__(self,
                 wrapped: ValueSupplierInterface,
                 caster: CasterInterface):
        """
        Args:
            wrapped: supplier to get values from
            caster: to use to cast values
        """
        self.wrapped = wrapped
        self.caster = caster

    def next(self, iteration):
        return self.caster.cast(self.wrapped.next(iteration))


class RandomRangeSupplier(ValueSupplierInterface):
    """
    Class that supplies values uniformly selected from specified bounds
    """

    def __init__(self,
                 start: Union[str, int, float],
                 end: Union[str, int, float],
                 precision: Union[str, int, float, None],
                 count_supplier: ValueSupplierInterface):
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
        self.format_str = '{:.' + str(precision) + 'f}'
        self.count_supplier = count_supplier

    def next(self, iteration):
        count = self.count_supplier.next(iteration)
        next_nums = [random.uniform(self.start, self.end) for _ in range(count)]
        if self.precision is not None:
            next_nums = [float(self.format_str.format(next_num)) for next_num in next_nums]
        if count == 1:
            return next_nums[0]
        return next_nums


class DistributionBackedSupplier(ValueSupplierInterface):
    """
    Class that supplies values selected from a distribution such as a Gaussian or Uniform distribution.

    @see datacraft.distributions
    """

    def __init__(self, distribution: Distribution):
        """
        Args:
            distribution: to use to generate values
        """
        self.distribution = distribution

    def next(self, _):
        return self.distribution.next_value()


class BufferedValueSupplier(ValueSupplierInterface):
    """
    Class for buffering the values from other suppliers. This allows the interaction
    of one supplier with the previous values of another supplier
    """

    def __init__(self, wrapped: ValueSupplierInterface, buffer_size: int):
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


class WeightedValueSupplier(ValueSupplierInterface):
    """
    Value supplier implementation for weighted values
    """

    def __init__(self,
                 choices: list,
                 weights: list,
                 count_supplier: ValueSupplierInterface):
        """
        Args:
            choices: list of choices to sample from
            weights: list of weights to use for random choice
            count_supplier: supplies number of values to sample
        """
        # may be passed raw data or a spec
        self.choices = choices
        self.weights = weights
        self.count_supplier = count_supplier

    def next(self, iteration):
        count = self.count_supplier.next(iteration)
        vals = random.choices(self.choices, self.weights, k=count)
        if count == 1:
            return vals[0]
        return vals


class ListCountSamplerSupplier(ValueSupplierInterface):
    """
    Supplies values by sampling from a list with hard min max and count
    """

    def __init__(self, data: Union[str, list],
                 count_supplier: ValueSupplierInterface,
                 join_with: Union[str, None] = ''):
        """
        Args:
            data: string or list to sample from
            count_supplier: to supply number of values to return
            join_with: how to join the values into a string, None means return as list
        """
        self.values = data
        self.count_supplier = count_supplier
        self.join_with = join_with

    def next(self, iteration):
        count = self.count_supplier.next(iteration)
        data = [random.sample(self.values, 1)[0] for _ in range(count)]
        if self.join_with is not None:
            return self.join_with.join([str(elem) for elem in data])
        return data


def list_stats_sampler_supplier(data: Union[str, list],
                                **kwargs) -> ValueSupplierInterface:
    """
    Creates a List Sampler that uses a stats based approach
    Args:
        data: to sample from
        **kwargs:

    Keyword Args:
        mean (float): mean number to sample
        min (int): min number of items
        max (int): max number of items
        stddev (float): standard deviation from mean
        join_with (bool): if the values should be joined as a string with this separator
        as_list (bool): if the values should be returned as a list
    Returns:

    """
    return _ListStatSamplerSupplier(data, **kwargs)


class _ListStatSamplerSupplier(ValueSupplierInterface):
    """
    Implementation for supplying values from a list by select a portion of them
    and optionally joining them by some delimiter
    """

    def __init__(self,
                 data: Union[str, list],
                 **kwargs):
        """
        Args:
            data: to sample from
            **kwargs: with config values for sampling
        """
        self.values = data
        self.mean = float(kwargs.get('mean', 1))
        self.min = int(kwargs.get('min', 1))
        self.max = int(kwargs.get('max', len(self.values)))
        # attempt to create a reasonable standard deviation
        if abs(int(self.mean - self.min)) < abs(int(self.mean - self.max)):
            lower_delta = abs(int(self.mean - self.min))
        else:
            lower_delta = abs(int(self.mean - self.max))
        self.stddev = float(kwargs.get('stddev', lower_delta))
        self.join_with = kwargs.get('join_with', ' ')
        self.as_list = kwargs.get('as_list', False)

    def next(self, _):
        if self.stddev == 0:
            count = int(self.mean)
        else:
            count = math.floor(random.gauss(self.mean, self.stddev))
        if count <= 0:
            count = 1
        if count > self.max:
            count = self.max
        if count < self.min:
            count = self.min
        # last check, cant sample more than exists
        if count > len(self.values):
            count = len(self.values)

        data = random.sample(self.values, count)
        if self.as_list:
            return data
        return self.join_with.join(data)


def list_value_supplier(data: list,
                        count_supplier: ValueSupplierInterface,
                        do_sampling: bool = False,
                        as_list: bool = False) -> ValueSupplierInterface:
    """
    Args:
        data: to rotate through
        count_supplier: to supply number of values to return
        do_sampling: if the list should be sampled from, default is to rotate through in order
        as_list: if results should be returned as a list
    """
    return _ListValueSupplier(data, count_supplier, do_sampling, as_list)


class _ListValueSupplier(ValueSupplierInterface):
    """
    Value Supplier implementation for supplying values from lists
    """

    def __init__(self,
                 data: list,
                 count_supplier: ValueSupplierInterface,
                 do_sampling: bool = False,
                 as_list: bool = False):
        """
        Args:
            data: to rotate through
            count_supplier: to supply number of values to return
            do_sampling: if the list should be sampled from, default is to rotate through in order
            as_list: if results should be returned as a list
        """
        self.values = data
        self.do_sampling = do_sampling
        self.count = count_supplier
        self.as_list = as_list

    def next(self, iteration):
        cnt = self.count.next(iteration)
        if self.do_sampling:
            values = random.sample(self.values, cnt)
        else:
            values = [self._value(iteration, i) for i in range(cnt)]
        if cnt == 1 and not self.as_list:
            return values[0]
        return values

    def _value(self, iteration, i):
        """ value for iteration i index i"""
        idx = (iteration + i) % len(self.values)
        return self.values[idx]


def weighted_values_explicit(choices: list,
                             weights: list,
                             count_supplier: Optional[ValueSupplierInterface] = None) -> ValueSupplierInterface:
    """
    Creates a weighted values supplier from the explicitly provided choices and weights. Count supplier is
    optional.

    Args:
        choices: list of choices to sample from
        weights: list of weights to use for random choice
        count_supplier: supplies number of values to sample

    Returns:
        ValueSupplierInterface that supplies values from choices according to weights
    """
    if count_supplier is None:
        count_supplier = SingleValue(1)
    return WeightedValueSupplier(choices, weights, count_supplier)


def iter_supplier(iterator: ResettableIterator) -> ValueSupplierInterface:
    """ Return ValueSupplierInterface for resettable iterator """
    return ResettableIteratorWrappedValueSupplier(iterator)


class ResettableIteratorWrappedValueSupplier(ValueSupplierInterface):
    """ class that wraps a generator to supply values from """

    def __init__(self, iterator: ResettableIterator):
        """
        Args:
            iterator: to supply values from
        """
        self.iter = iterator

    def next(self, iteration):
        try:
            return next(self.iter)
        except StopIteration:
            self.iter.reset()
            return next(self.iter)
