"""
Factory like module for core supplier related functions.
"""
import json
from typing import Union, List, Dict, Any

from . import types, casters, distributions, utils
from .casters import from_config
from .exceptions import SpecException
from .supplier.common import (SingleValue, MultipleValueSupplier, RotatingSupplierList, DecoratedSupplier,
                              CastingSupplier, RandomRangeSupplier, DistributionBackedSupplier,
                              BufferedValueSupplier, ListCountSamplerSupplier,
                              list_stats_sampler, list_value_supplier, weighted_values_explicit)
from .supplier.combine import combine_supplier
from .supplier.model import Distribution, ValueSupplierInterface


def values(spec: Any, loader=None, **kwargs) -> ValueSupplierInterface:
    """
    Based on data, return the appropriate values supplier. data can be a spec, constant, list, or dict.
    or just the raw data

    Args:
        spec: to load values from, or raw data itself
        loader: if needed
        **kwargs: extra kwargs to add to config

    Returns:
        the values supplier for the spec

    Examples:
        >>> import datagen
        >>> spec = {"type": "values", "data": [1,2,3,5,8,13]}
        >>> fib_supplier = datagen.suppliers.values(spec)
        >>> fib_supplier = datagen.suppliers.values([1,2,3,5,8,13])
        >>> weights =  {"1": 0.1, "2": 0.2, "3": 0.1, "4": 0.2, "5": 0.1, "6": 0.2, "7": 0.1}
        >>> mostly_even_supplier = datagen.suppliers.values(weights)
    """
    # shortcut notations no type, or data, the spec is the data
    if _data_not_in_spec(spec):
        data = spec
    else:
        data = spec['data']

    config = utils.load_config(spec, loader, **kwargs)
    do_sampling = utils.is_affirmative('sample', config, default=types.get_default('sample_mode'))

    if isinstance(data, list):
        # this supplier can handle the count param itself, so just return it
        return _value_list(data, config, do_sampling)
    if isinstance(data, dict):
        if do_sampling:
            raise SpecException('Cannot do sampling on weighted values: ' + json.dumps(spec))
        supplier = weighted_values(data)
    else:
        supplier = single_value(data)

    # Check for count param
    if 'count' in config or 'count_dist' in config:
        return MultipleValueSupplier(supplier, count_supplier_from_config(config))
    return supplier


def _data_not_in_spec(spec):
    """check to see if the data element is defined for this spec """
    if isinstance(spec, dict):
        return 'data' not in spec
    return True


def count_supplier_from_data(data: Union[int, List[int], Dict[str, float], Distribution]) -> ValueSupplierInterface:
    """
    generates a supplier for the count parameter based on the type of the data

    valid data for counts:

     * integer i.e. 1, 7, 99

     * list of integers: [1, 7, 99], [1], [1, 2, 1, 2, 3]

     * weighted map, where keys are numeric strings: {"1": 0.6, "2": 0.4}

     * datagen.Distribution i.e. normal, gauss

    Args:
        data: that specifies how the count should be generated

    Returns:
        a value supplier for the count

    Raises:
        SpecException if unable to determine the type of the data
    """
    if isinstance(data, list):
        supplier = _value_list(data, None, False)
    elif isinstance(data, dict):
        supplier = weighted_values(data)
    elif isinstance(data, Distribution):
        supplier = cast_supplier(distribution_supplier(data), cast_to='int')
    else:
        try:
            supplier = single_value(int(data))
        except ValueError as value_error:
            raise SpecException(f'Invalid count param: {data}') from value_error

    return supplier


def count_supplier_from_config(config: dict) -> ValueSupplierInterface:
    """
    creates a count supplier from the config, if the count param is defined, otherwise uses default of 1

    optionally can specify count or count_dist.

    valid data for counts:
     * integer i.e. 1, 7, 99
     * list of integers: [1, 7, 99], [1], [1, 2, 1, 2, 3]
     * weighted map, where keys are numeric strings: {"1": 0.6, "2": 0.4}

    count_dist will be interpreted as a distribution i.e:

    Args:
        config: to use

    Returns:
        a count supplier

    Examples:
        >>> import datagen
        >>> config = {"count_dist": "uniform(start=10, end=100)"}
        >>> count_supplier = datagen.suppliers.count_supplier_from_config(config)
    """
    data = 1  # type: Any
    if config and 'count' in config:
        data = config['count']
    if config and 'count_dist' in config:
        data = distributions.from_string(config['count_dist'])
    return count_supplier_from_data(data)


def single_value(data: Any) -> ValueSupplierInterface:
    """
    Creates value supplier for the single value

    Args:
        data: constant data to return on every iteration

    Returns:
        value supplier for the single value
    Examples:
        >>> import datagen
        >>> single_int_supplier = datagen.suppliers.single_value(42)
        >>> single_str_supplier = datagen.suppliers.single_value("42")
        >>> single_float_supplier = datagen.suppliers.single_value(42.42)
    """
    return SingleValue(data)


def array_supplier(wrapped: ValueSupplierInterface,
                   count_config: dict) -> ValueSupplierInterface:
    """
    Wraps an existing supplier and always returns an array/list of elements, uses count config to determine
    number of items in the list

    Args:
        wrapped: the underlying supplier
        count_config: how to determine the number of elements to include in the list

    Returns:
        The value supplier

    Examples:
        >>> import datagen
        >>> config = {"count_dist": "normal(mean=2, stddev=1)"}
        >>> pet_supplier = datagen.suppliers.values(["dog", "cat", "hamster", "pig", "rabbit", "horse"])
        >>> returns_mostly_two = datagen.suppliers.array_supplier(pet_supplier, config)
        >>> pet_array = returns_mostly_two.next(0)
    """
    return MultipleValueSupplier(wrapped, count_supplier_from_config(count_config))


def from_list_of_suppliers(supplier_list: List[ValueSupplierInterface],
                           modulate_iteration: bool = True) -> ValueSupplierInterface:
    """
    Returns a supplier that rotates through the provided suppliers incrementally

    Args:
        supplier_list: to rotate through
        modulate_iteration: if the iteration number should be moded by the index of the supplier

    Returns:
        a supplier for these suppliers

    Examples:
        >>> import datagen
        >>> nice_pet_supplier = datagen.suppliers.values(["dog", "cat", "hamster", "pig", "rabbit", "horse"])
        >>> mean_pet_supplier = datagen.suppliers.values(["alligator", "cobra", "mongoose", "killer bee"])
        >>> pet_supplier = datagen.suppliers.from_list_of_suppliers([nice_pet_supplier, mean_pet_supplier])
    """
    return RotatingSupplierList(supplier_list, modulate_iteration)


def _value_list(data: list,
                config: dict = None,
                do_sampling: bool = False) -> ValueSupplierInterface:
    """
    creates a value list supplier

    Args:
        data: for the supplier
        config: config with optional count param
        do_sampling: if the data should be sampled instead of iterated through

    Returns:
        the supplier

    """
    if config is None:
        config = {}
    as_list = utils.is_affirmative('as_list', config)
    return list_value_supplier(data, count_supplier_from_config(config), do_sampling, as_list)


def weighted_values(data: dict, config: dict = None) -> ValueSupplierInterface:
    """
    Creates a weighted value supplier from the data, which is a mapping of value to the weight is should represent.

    Args:
        data: for the supplier
        config: optional config (Default value = None)

    Returns:
        the supplier

    Raises:
        SpecException if data is empty

    Examples:
        >>> import datagen
        >>> weights = {"dog": 0.5, "cat": 0.2, "bunny": 0.1, "hamster": 0.1, "pig": 0.05, "snake": 0.04, "rat": 0.01}
        >>> weighted_pet_supplier = datagen.suppliers.weighted_values(weights)
        >>> most_likely_a_dog = weighted_pet_supplier.next(0)
    """
    if len(data) == 0:
        raise SpecException('Invalid Weights, no values defined')
    choices = list(data.keys())
    weights = list(data.values())
    if not isinstance(weights[0], float):
        raise SpecException('Invalid type for weights: ' + str(type(weights[0])))
    return weighted_values_explicit(choices, weights, count_supplier_from_config(config))


def combine(suppliers, config=None):
    """
    Creates a value supplier that will combine the outputs of the provided suppliers in order. The default is to
    join the values with an empty string. Provide the join_with config param to specify a different string to
    join the values with. Set as_list to true, if the values should be returned as a list and not joined


    Args:
        suppliers: to combine value for
        config: for the combiner (Default value = None)

    Returns:
        the supplier

    Examples:
        >>> import datagen
        >>> pet_supplier = datagen.suppliers.values(["dog", "cat", "hamster", "pig", "rabbit", "horse"], sample=True)
        >>> job_supplier = datagen.suppliers.values(["breeder", "trainer", "fighter", "wrestler"], sample=True)
        >>> interesting_jobs = datagen.suppliers.combine([pet_supplier, job_supplier], {'join_with': ' '})
        >>> next_career = interesting_jobs.next(0)
    """
    if config is None:
        config = {}
    as_list = utils.is_affirmative('as_list', config)
    join_with = config.get('join_with', types.get_default('combine_join_with'))
    return combine_supplier(suppliers, as_list, join_with)


def random_range(start: Union[str, int, float],
                 end: Union[str, int, float],
                 precision: Union[str, int, float] = None,
                 count: Union[int, List[int], Dict[str, float], Distribution] = 1) -> ValueSupplierInterface:
    """
    Creates a random range supplier for the start and end parameters with the given precision
    (number of decimal places)

    Args:
        start: of range
        end: of range
        precision: number of decimal points to keep
        count: number of elements to return, default is one

    Returns:
        the value supplier for the range

    Examples:
        >>> range_supplier = datagen.suppliers.random_range(5, 25, precision=3)
        >>> # should be between 5 and 25 with 3 decimal places
        >>> next_value = range_supplier.next(0))
    """
    return RandomRangeSupplier(start, end, precision, count_supplier_from_data(count))


def list_stat_sampler(data: Union[str, list],
                      config: dict) -> ValueSupplierInterface:
    """
    sample from list (or string) with stats based params

    Args:
        data: list to select subset from
        config: with minimal of mean specified

    Returns:
        the supplier

    Examples:
        >>> import datagen
        >>> stats_config = {"mean": 2, "stddev": 1}
        >>> pet_list = ["dog", "cat", "hamster", "pig", "rabbit", "horse"]
        >>> pet_supplier = datagen.suppliers.list_stat_sampler(pet_list, stats_config)
        >>> new_pets = pet_supplier.next(0)

        >>> char_config = {"min": 2, "mean": 4, "max": 8}
        >>> char_supplier = datagen.suppliers.list_stat_sampler("#!@#$%^&*()_-~", char_config)
        >>> two_to_eight_chars = char_supplier.next(0)
    """
    config['as_list'] = utils.is_affirmative('as_list', config, False)
    return list_stats_sampler(data, **config)


def list_count_sampler(data: list, config: dict) -> ValueSupplierInterface:
    """
    Samples N elements from data list based on config.  If count is provided,
    each iteration exactly count elements will be returned.  If only min is provided,
    between min and the total number of elements will be provided. If only max is provided,
    between one and max elements will be returned. Specifying both min and max will provide
    a sample containing a number of elements in this range.


    Args:
        data: list to select subset from
        config: with minimal of count or min and max supplied

    Returns:
        the supplier

    Examples:
        >>> import datagen
        >>> count_config = {"min": 2, "max": 5}
        >>> pet_list = ["dog", "cat", "hamster", "pig", "rabbit", "horse"]
        >>> pet_supplier = datagen.suppliers.list_count_sampler(pet_list, count_config)
        >>> new_pets = pet_supplier.next(0)
    """
    if 'count' in config or 'count_dist' in config:
        count_supplier = count_supplier_from_config(config)
    else:
        min_cnt = int(config.get('min', 1))
        max_cnt = int(config.get('max', len(data))) + 1
        count_range = list(range(min_cnt, max_cnt))
        count_supplier = _value_list(count_range, None, True)
    return ListCountSamplerSupplier(data, count_supplier, config.get('join_with', None))


def distribution_supplier(distribution: Distribution) -> ValueSupplierInterface:
    """
    creates a ValueSupplier that uses the given distribution to generate values

    Args:
        distribution: to use

    Returns:
        the value supplier
    """
    wrapped = DistributionBackedSupplier(distribution)
    # buffer the values
    return buffered(wrapped, {})


def is_decorated(field_spec: dict) -> bool:
    """
    is this spec a decorated one

    Args:
        field_spec: to check

    Returns:
        true or false
    """
    if 'config' not in field_spec:
        return False
    config = field_spec['config']
    return 'prefix' in config or 'suffix' in config or 'quote' in config


def decorated(field_spec: dict, supplier: ValueSupplierInterface) -> ValueSupplierInterface:
    """
    Creates a decorated supplier around the provided one

    Args:
        field_spec: the spec
        supplier: the supplier to decorate

    Returns:
        the decorated supplier
    """
    return DecoratedSupplier(field_spec.get('config', {}), supplier)


def is_cast(field_spec: dict) -> bool:
    """
    is this spec requires casting

    Args:
        field_spec: to check

    Returns:
        true or false
    """
    if not isinstance(field_spec, dict):
        return False
    config = field_spec.get('config', {})
    return 'cast' in config


def cast_supplier(supplier: ValueSupplierInterface,
                  field_spec: dict = None,
                  cast_to: str = None) -> ValueSupplierInterface:
    """
    Provides a cast_supplier either from config or from explicit cast_to

    Args:
        supplier: to cast results of
        field_spec: to look up cast config from
        cast_to: explicit cast type to use

    Returns:
        the casting supplier
    """

    if cast_to:
        caster = casters.get(cast_to)
    else:
        if field_spec is None:
            config = {}
        else:
            config = field_spec.get('config', {})
        caster = from_config(config)
    return CastingSupplier(supplier, caster)


def is_buffered(field_spec: dict) -> bool:
    """
    Should the values for this spec be buffered

    Args:
        field_spec: to check

    Returns:
        true or false

    """
    config = field_spec.get('config', {})
    return 'buffer_size' in config or utils.is_affirmative('buffer', config)


def buffered(wrapped: ValueSupplierInterface, field_spec: dict) -> ValueSupplierInterface:
    """
    Creates a Value Supplier that buffers the results of the wrapped supplier allowing the retrieval

    Args:
        wrapped: the Value Supplier to buffer values for
        field_spec: to check

    Returns:
        a buffered value supplier
    """
    config = field_spec.get('config', {})
    buffer_size = int(config.get('buffer_size', 10))
    return BufferedValueSupplier(wrapped, buffer_size)
