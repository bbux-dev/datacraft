"""
Factory like module for core supplier related functions.
"""

import json
import random
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
    if 'data' not in spec:
        data = spec
    else:
        data = spec['data']

    config = load_config(spec, loader)
    do_sampling = is_affirmative('sample', config)

    if isinstance(data, list):
        # this supplier can handle the count param itself, so just return it
        return value_list(data, do_sampling, config.get('count', 1))
    if isinstance(data, dict):
        if do_sampling:
            raise SpecException('Cannot do sampling on weighted values: ' + json.dumps(spec))
        supplier = weighted_values(data)
    else:
        supplier = single_value(data)

    # Check for count param
    if 'count' in config:
        return _MultipleValueSupplier(supplier, config['count'])
    return supplier


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


class _MultipleValueSupplier(ValueSupplierInterface):
    """
    Supplier that generates list of values based on count parameter
    """

    def __init__(self, wrapped, count):
        self.wrapped = wrapped
        self.count = int(count)

    def next(self, iteration):
        return [self.wrapped.next(iteration + i) for i in range(self.count)]


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


def value_list(data, do_sampling=False, count=1):
    """
    creates a value list supplier
    :param data: for the supplier
    :param do_sampling: if the data should be sampled instead of iterated through
    :param count: number of values to return on each iteration
    :return: the supplier
    """
    return ListValueSupplier(data, do_sampling, count)


def weighted_values(data):
    """
    creates a weighted value supplier
    :param data: for the supplier
    :return: the supplier
    """
    return WeightedValueSupplier(data)


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


def list_count_sampler(data, config):
    """
    sample from list with counts
    :param data: list to select subset from
    :param config: with minimal of count or min and max supplied
    :return: the supplier
    """
    return ListCountSamplerSupplier(data, config)


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
    return any(key in config for key in ['cast', 'cast_as', 'cast_to'])


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
    Class that supplies random ranges between specified bounds
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
