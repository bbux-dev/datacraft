"""
Factory like module for core supplier related functions.
"""
import types
from typing import Union, Dict
import json
import random
from collections import deque
from .exceptions import SpecException
from .utils import load_config, is_affirmative, get_caster
from .supplier.list_values import ListValueSupplier
from .supplier.combine import CombineValuesSupplier
from .supplier.weighted_values import WeightedValueSupplier
from .supplier.weighted_refs import WeightedRefsSupplier
from .supplier.list_stat_sampler import ListStatSamplerSupplier
from .supplier.list_count_sampler import ListCountSamplerSupplier
from .supplier.value_supplier import ValueSupplierInterface
from . import casters


def values(spec, loader=None):
    """
    Based on data, return the appropriate values supplier
    """
    # shortcut notations no type, or data, the spec is the data
    if _data_not_in_spec(spec):
        data = spec
    else:
        data = spec['data']

    config = load_config(spec, loader)
    do_sampling = is_affirmative('sample', config)

    if isinstance(data, list):
        # this supplier can handle the count param itself, so just return it
        return value_list(data, config.get('count', 1), do_sampling)
    if isinstance(data, dict):
        if do_sampling:
            raise SpecException('Cannot do sampling on weighted values: ' + json.dumps(spec))
        supplier = weighted_values(data)
    else:
        supplier = single_value(data)

    # Check for count param
    if 'count' in config:
        return _MultipleValueSupplier(supplier, count_supplier_from_data(config['count']))
    return supplier


def _data_not_in_spec(spec):
    if isinstance(spec, dict):
        return 'data' not in spec
    return True


def count_supplier_from_data(data):
    """ generates a supplier for the count parameter based on the type of the data """
    if isinstance(data, list):
        supplier = value_list(data, 1, False)
    elif isinstance(data, dict):
        supplier = weighted_values(data)
    else:
        try:
            supplier = single_value(int(data))
        except ValueError as value_error:
            raise SpecException(f'Invalid count param: {data}') from value_error

    return supplier


def count_supplier_from_config(config: Dict):
    """
    creates a count supplier from the config, if the count param is defined, otherwise uses default of 1
    :param config: to use
    :return: a count supplier
    """
    data = 1
    if config and 'count' in config:
        data = config['count']
    return count_supplier_from_data(data)


class _SingleValue(ValueSupplierInterface):
    """
    Encapsulates supplier that only returns a static value
    """

    def __init__(self, data):
        self.data = data

    def next(self, _):
        return self.data


def single_value(data):
    """ Creates value supplier for the single value """
    return _SingleValue(data)


def array_supplier(wrapped: ValueSupplierInterface, count_config):
    """ returns a supplier that always returns an array of elements  based on the count config supplied """
    return _MultipleValueSupplier(wrapped, count_supplier_from_data(count_config))


class _MultipleValueSupplier(ValueSupplierInterface):
    """
    Supplier that generates list of values based on count parameter
    """

    def __init__(self, wrapped: ValueSupplierInterface, count_supplier: ValueSupplierInterface):
        self.wrapped = wrapped
        self.count_supplier = count_supplier

    def next(self, iteration):
        count = self.count_supplier.next(iteration)
        return [self.wrapped.next(iteration + i) for i in range(count)]


def from_list_of_suppliers(supplier_list, modulate_iteration):
    """
    Returns a supplier that rotates through the provided suppliers incrementally
    :param supplier_list: to rotate through
    :param modulate_iteration: if the iteration number should be moded by the index of the supplier
    :return: a supplier for these suppliers
    """
    return RotatingSupplierList(supplier_list, modulate_iteration)


class RotatingSupplierList(ValueSupplierInterface):
    """
    Class that rotates through a list of suppliers incrementally to provide the next value
    """

    def __init__(self, suppliers, modulate_iteration):
        """
        :param suppliers: list of suppliers to rotate through
        :param modulate_iteration: if the iteration should be split evenly across all suppliers
        """
        self.suppliers = suppliers
        self.modulate_iteration = modulate_iteration

    def next(self, iteration):
        idx = iteration % len(self.suppliers)
        if self.modulate_iteration:
            modulated_iteration = int(iteration / len(self.suppliers))
            return self.suppliers[idx].next(modulated_iteration)
        return self.suppliers[idx].next(iteration)


def value_list(data, count: Union[int, list, dict], do_sampling=False):
    """
    creates a value list supplier
    :param data: for the supplier
    :param do_sampling: if the data should be sampled instead of iterated through
    :param count: number of values to return on each iteration, or list, or weighted mapping
    :return: the supplier
    """
    return ListValueSupplier(data, count_supplier_from_data(count), do_sampling)


def weighted_values(data, config=None):
    """
    creates a weighted value supplier
    :param data: for the supplier
    :param config: optional config
    :return: the supplier
    """
    return WeightedValueSupplier(data, count_supplier_from_config(config))


def combine(suppliers, config=None):
    """
    combine supplier
    :param suppliers: to combine value for
    :param config: for the combiner
    :return: the supplier
    """
    return CombineValuesSupplier(suppliers, config)


def weighted_ref(key_supplier, values_map):
    """
    weighted refs supplier
    :param key_supplier: supplies weighted keys
    :param values_map: map of key to supplier for that key
    :return: the supplier
    """
    return WeightedRefsSupplier(key_supplier, values_map)


def list_stat_sampler(data, config):
    """
    sample from list with stats based params
    :param data: list to select subset from
    :param config: with minimal of mean specified
    :return: the supplier
    """
    return ListStatSamplerSupplier(data, config)


def list_count_sampler(data: list, config: dict):
    """
    sample from list with counts
    :param data: list to select subset from
    :param config: with minimal of count or min and max supplied
    :return: the supplier
    """
    count = config.get('count')
    if count is not None:
        count_supplier = count_supplier_from_data(count)
    else:
        min_cnt = int(config.get('min', 1))
        max_cnt = int(config.get('max', len(data))) + 1
        count_range = list(range(min_cnt, max_cnt))
        count_supplier = value_list(count_range, 1, True)
    return ListCountSamplerSupplier(data, count_supplier, config.get('join_with', None))


def is_decorated(field_spec):
    """
    is this spec a decorated one
    :param field_spec: to check
    :return: true or false
    """
    if 'config' not in field_spec:
        return False
    config = field_spec.get('config')
    return 'prefix' in config or 'suffix' in config or 'quote' in config


class DecoratedSupplier(ValueSupplierInterface):
    """
    Class used to add additional data to other suppliers output, such as a
    prefix or suffix or to surround the output with quotes
    """

    def __init__(self, config, supplier):
        self.prefix = config.get('prefix', '')
        self.suffix = config.get('suffix', '')
        self.quote = config.get('quote', '')
        self.wrapped = supplier

    def next(self, iteration):
        value = self.wrapped.next(iteration)
        # todo: cache mapping for efficiency?
        return f'{self.quote}{self.prefix}{value}{self.suffix}{self.quote}'


def decorated(field_spec, supplier):
    """
    Creates a decorated supplier around the provided on
    :param field_spec: the spec
    :param supplier: the supplier to decorate
    :return: the decorated supplier
    """
    return DecoratedSupplier(field_spec.get('config'), supplier)


class CastingSupplier(ValueSupplierInterface):
    """
    Class that just casts the results of other suppliers
    """

    def __init__(self, wrapped, caster):
        self.wrapped = wrapped
        self.caster = caster

    def next(self, iteration):
        return self.caster.cast(self.wrapped.next(iteration))


def is_cast(field_spec):
    """
    is this spec requires casting
    :param field_spec: to check
    :return: true or false
    """
    if not isinstance(field_spec, dict):
        return False
    config = field_spec.get('config', {})
    return 'cast' in config


def cast_supplier(supplier, field_spec, cast_to=None):
    """
    Provides a cast_supplier either from config or from explicit cast_to
    :param supplier: to cast results of
    :param field_spec: to look up cast config from
    :param cast_to: explicit cast type to use
    :return: the casting supplier
    """
    if cast_to:
        caster = casters.get(cast_to)
    else:
        caster = get_caster(field_spec.get('config'))
    return CastingSupplier(supplier, caster)


class RandomRangeSupplier(ValueSupplierInterface):
    """
    Class that supplies values uniformly selected from specified bounds
    """

    def __init__(self, start, end, precision, count=1):
        self.start = float(start)
        self.end = float(end)
        self.precision = precision
        self.format_str = '{: .' + str(precision) + 'f}'
        self.count = count

    def next(self, iteration):
        next_nums = [random.uniform(self.start, self.end) for _ in range(self.count)]
        if self.precision is not None:
            next_nums = [self.format_str.format(next_num) for next_num in next_nums]
        if self.count == 1:
            return next_nums[0]
        return next_nums


def random_range(start, end, precision=None, count=1):
    return RandomRangeSupplier(start, end, precision, count)


class GaussRangeSupplier(ValueSupplierInterface):
    """
    Class that supplies values selected from a normal distribution
    """

    def __init__(self, mean, stddev, precision, count=1):
        self.mean = float(mean)
        self.stddev = float(stddev)
        self.precision = precision
        self.format_str = '{: .' + str(precision) + 'f}'
        self.count = count

    def next(self, iteration):
        next_nums = [random.gauss(self.mean, self.stddev) for _ in range(self.count)]
        if self.precision is not None:
            next_nums = [self.format_str.format(next_num) for next_num in next_nums]
        if self.count == 1:
            return next_nums[0]
        return next_nums


def gauss_range(mean, stddev, precision=None, count=1):
    return GaussRangeSupplier(mean, stddev, precision, count)


def is_buffered(field_spec):
    """
    Should the values for this spec be buffered
    :param field_spec: to check
    :return: true or false
    """
    config = field_spec.get('config', {})
    return 'buffer_size' in config or is_affirmative('buffer', config)


def buffered(wrapped: ValueSupplierInterface, field_spec):
    """
    Creates a Value Supplier that buffers the results of the wrapped supplier
    :param wrapped: the Value Supplir to buffer values for
    :param field_spec: to check
    :return:
    """
    config = field_spec.get('config', {})
    buffer_size = int(config.get('buffer_size', 10))
    return _BufferedValueSuppier(wrapped, buffer_size)


class _BufferedValueSuppier(ValueSupplierInterface):
    """
    Class for buffering the values from other suppliers. This allows the interaction
    of one supplier with the previous values of another supplier
    """

    def __init__(self, wrapped: ValueSupplierInterface, buffer_size: int):
        self.wrapped = wrapped
        self.buffer = deque(maxlen=buffer_size)
        self.current = -1

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
