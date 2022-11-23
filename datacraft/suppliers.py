"""
Factory like module for core supplier related functions.
"""
import datetime
import os
import json
import logging
from typing import Union, List, Dict, Any

import datacraft.supplier.ranges
from . import registries, casters, distributions, utils, template_engines
from .exceptions import SpecException
from .supplier.common import (SingleValue, MultipleValueSupplier, RotatingSupplierList, DecoratedSupplier,
                              CastingSupplier, RandomRangeSupplier, DistributionBackedSupplier,
                              BufferedValueSupplier, ListCountSamplerSupplier,
                              list_stats_sampler_supplier, list_value_supplier, weighted_values_explicit, iter_supplier)
from .supplier.model import Distribution, ValueSupplierInterface, ResettableIterator
from .supplier.combine import combine_supplier
from .supplier.calculate import calculate_supplier
from .supplier.date import date_supplier, uniform_date_timestamp, epoch_date_supplier
from .supplier.csv import load_csv_data, csv_supplier
from .supplier.uuid import uuid_supplier
from .supplier.unicode import unicode_range_supplier
from .supplier.templated import templated_supplier
from .supplier import network, ranges
from .supplier.strings import cut_supplier

_log = logging.getLogger(__name__)


def constant(data: Any) -> ValueSupplierInterface:
    """
    Creates value supplier for the single value

    Args:
        data: constant data to return on every iteration

    Returns:
        value supplier for the single value
    Examples:
        >>> import datacraft
        >>> single_int_supplier = datacraft.suppliers.constant(42)
        >>> single_str_supplier = datacraft.suppliers.constant("42")
        >>> single_float_supplier = datacraft.suppliers.constant(42.42)
    """
    return SingleValue(data)


def values(spec: Any, **kwargs) -> ValueSupplierInterface:
    """
    Based on data, return the appropriate values supplier. data can be a spec, constant, list, or dict.
    or just the raw data

    Args:
        spec: to load values from, or raw data itself
        **kwargs: extra kwargs to add to config

    Keyword Args:
        as_list (bool): if data should be returned as a list
        sample (bool): if the data should be sampled instead of iterated through incrementally
        count: constant, list, or weighted map
        count_dist (str): distribution in named param function style format

    Returns:
        the values supplier for the spec

    Examples:
        >>> import datacraft
        >>> raw_spec = {"type": "values", "data": [1,2,3,5,8,13]}
        >>> fib_supplier = datacraft.suppliers.values(raw_spec)
        >>> fib_supplier = datacraft.suppliers.values([1,2,3,5,8,13])
        >>> fib_supplier.next(0)
        1
        >>> weights =  {"1": 0.1, "2": 0.2, "3": 0.1, "4": 0.2, "5": 0.1, "6": 0.2, "7": 0.1}
        >>> mostly_even_supplier = datacraft.suppliers.values(weights)
        >>> mostly_even_supplier.next(0)
        '4'
    """
    # shortcut notations no type, or data, the spec is the data
    if _data_not_in_spec(spec):
        data = spec
        config = {}
    else:
        data = spec.get('data')
        config = spec.get('config', {})
    kwargs.update(config)

    if isinstance(data, list):
        # this supplier can handle the count param itself, so just return it
        return list_values(data, **kwargs)
    if isinstance(data, dict):
        supplier = weighted_values(data)
    else:
        supplier = constant(data)

    # Check for count param
    # if 'count' in kwargs or 'count_dist' in kwargs:
    #     return MultipleValueSupplier(supplier, count_supplier(**kwargs))
    return supplier


def _data_not_in_spec(spec):
    """check to see if the data element is defined for this spec """
    if isinstance(spec, dict):
        return 'data' not in spec
    return True


def count_supplier(**kwargs) -> ValueSupplierInterface:
    """
    creates a count supplier from the config, if the count param is defined, otherwise uses default of 1

    optionally can specify count or count_dist.

    valid data for counts:
     * integer i.e. 1, 7, 99
     * list of integers: [1, 7, 99], [1], [1, 2, 1, 2, 3]
     * weighted map, where keys are numeric strings: {"1": 0.6, "2": 0.4}

    count_dist will be interpreted as a distribution i.e:

    Keyword Args:
        count: constant, list, or weighted map
        data: alias for count
        count_dist (str): distribution in named param function style format

    Returns:
        a count supplier

    Examples:
        >>> import datacraft
        >>> counts = datacraft.suppliers.count_supplier(count_dist="uniform(start=10, end=100)")
    """
    data = 1  # type: Any
    if 'count' in kwargs:
        data = kwargs['count']
    if 'data' in kwargs:
        data = kwargs['data']
    if 'count_dist' in kwargs:
        data = distributions.from_string(kwargs['count_dist'])

    if isinstance(data, list):
        supplier = list_values(data)
    elif isinstance(data, dict):
        supplier = cast(weighted_values(data), cast_to='int')
    elif isinstance(data, Distribution):
        supplier = cast(distribution_supplier(data), cast_to='int')
    else:
        try:
            supplier = constant(int(data))
        except ValueError as value_error:
            raise ValueError(f'Invalid count param: {data}') from value_error

    return supplier


def array_supplier(wrapped: ValueSupplierInterface,
                   **kwargs) -> ValueSupplierInterface:
    """
    Wraps an existing supplier and always returns an array/list of elements, uses count config to determine
    number of items in the list

    Args:
        wrapped: the underlying supplier

    Keyword Args:
        count: constant, list, or weighted map
        data: alias for count
        count_dist: distribution in named param function style format

    Returns:
        The value supplier

    Examples:
        >>> import datacraft
        >>> pet_supplier = datacraft.suppliers.values(["dog", "cat", "hamster", "pig", "rabbit", "horse"])
        >>> returns_mostly_two = datacraft.suppliers.array_supplier(pet_supplier, count_dist="normal(mean=2, stddev=1)")
        >>> pet_array = returns_mostly_two.next(0)
    """
    return MultipleValueSupplier(wrapped, count_supplier(**kwargs))


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
        >>> import datacraft
        >>> nice_pet_supplier = datacraft.suppliers.values(["dog", "cat", "hamster", "pig", "rabbit", "horse"])
        >>> mean_pet_supplier = datacraft.suppliers.values(["alligator", "cobra", "mongoose", "killer bee"])
        >>> pet_supplier = datacraft.suppliers.from_list_of_suppliers([nice_pet_supplier, mean_pet_supplier])
        >>> pet_supplier.next(0)
        'dog'
        >>> pet_supplier.next(1)
        'alligator'
    """
    return RotatingSupplierList(supplier_list, modulate_iteration)


def alter(supplier, **kwargs) -> ValueSupplierInterface:
    """
    Covers multiple suppliers that alter values if configured to do so through kwargs: cast, buffer, and decorate

    Args:
        supplier: to alter if configured to do so

    Keyword Args:
        cast (str): caster to apply
        prefix (str): prefix to prepend to value, default is ''
        suffix (str): suffix to append to value, default is ''
        quote (str): string to both append and prepend to value, default is ''
        buffer (bool): if the values should be buffered
        buffer_size (int): size of buffer to use

    Returns:
        supplier with alterations
    """
    if _is_cast(**kwargs):
        supplier = cast(supplier, cast_to=kwargs.get('cast'))  # type: ignore
    if _is_decorated(**kwargs):
        supplier = decorated(supplier, **kwargs)
    if _is_buffered(**kwargs):
        supplier = buffered(supplier, **kwargs)
    if _wrap_with_multiple_value(supplier, **kwargs):
        return MultipleValueSupplier(supplier, count_supplier(**kwargs))
    return supplier


def _wrap_with_multiple_value(supplier, **kwargs):
    """ checks if this supplier should be wrapped with multiple values supplier """
    has_count = 'count' in kwargs or 'count_dist' in kwargs
    as_list = utils.is_affirmative('as_list', kwargs)
    return has_count and as_list


def _is_decorated(**kwargs) -> bool:
    """ is this spec a decorated one """
    return any(key in kwargs for key in ['prefix', 'suffix', 'quote'])


def _is_cast(**kwargs) -> bool:
    """ Does this spec require casting """
    return 'cast' in kwargs


def _is_buffered(**kwargs) -> bool:
    """ Should the values for this spec be buffered """
    return 'buffer_size' in kwargs or utils.is_affirmative('buffer', kwargs)


def list_values(data: list, **kwargs) -> ValueSupplierInterface:
    """
    creates a Value supplier for the list of provided data

    Args:
        data: for the supplier

    Keyword Args:
        as_list (bool): if data should be returned as a list
        sample (bool): if the data should be sampled instead of iterated through incrementally
        count: constant, list, or weighted map
        count_dist (str): distribution in named param function style format

    Returns:
        the ValueSupplierInterface for the data list
    """
    as_list = utils.is_affirmative('as_list', kwargs)
    sample = utils.is_affirmative('sample', kwargs, default=registries.get_default('sample_mode'))
    return list_value_supplier(data, count_supplier(**kwargs), sample, as_list)


def weighted_values(data: dict, config: Union[dict, None] = None) -> ValueSupplierInterface:
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
        >>> import datacraft
        >>> pets = {
        ... "dog": 0.5, "cat": 0.2, "bunny": 0.1, "hamster": 0.1, "pig": 0.05, "snake": 0.04, "_NULL_": 0.01
        ... }
        >>> weighted_pet_supplier = datacraft.suppliers.weighted_values(pets)
        >>> most_likely_a_dog = weighted_pet_supplier.next(0)
    """
    if len(data) == 0:
        raise SpecException('Invalid Weights, no values defined')
    if config is None:
        config = {}
    replacements = {
        '_NONE_': None,
        '_NULL_': None,
        '_NIL_': None,
        '_TRUE_': True,
        '_FALSE_': False
    }
    choices = []
    for key in data.keys():
        if key in replacements:
            choices.append(replacements.get(key))
        else:
            choices.append(key)
    weights = list(data.values())
    if not isinstance(weights[0], float):
        raise SpecException('Invalid type for weights: ' + str(type(weights[0])))
    return weighted_values_explicit(choices, weights, count_supplier(**config))


def random_range(start: Union[str, int, float],
                 end: Union[str, int, float],
                 precision: Union[str, int, float, None] = None,
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
        >>> num_supplier = datacraft.suppliers.random_range(5, 25, precision=3)
        >>> # should be between 5 and 25 with 3 decimal places
        >>> num_supplier.next(0)
        8.377
    """
    return RandomRangeSupplier(start, end, precision, count_supplier(data=count))


def list_stats_sampler(data: Union[str, list],
                       **kwargs) -> ValueSupplierInterface:
    """
    sample from list (or string) with stats based params

    Args:
        data: list to select subset from

    Keyword Args:
        mean (float): mean number of items/characters to produce
        stddev (float): standard deviation from the mean
        count (int): number of elements in list/characters to use
        count_dist (str): count distribution to use
        min (int): minimum number of items/characters to return
        max (int): maximum number of items/characters to return

    Returns:
        the supplier

    Examples:
        >>> import datacraft
        >>> pet_list = ["dog", "cat", "hamster", "pig", "rabbit", "horse"]
        >>> pet_supplier = datacraft.suppliers.list_stats_sampler(pet_list, mean=2, stddev=1)
        >>> new_pets = pet_supplier.next(0)

        >>> char_config = {"min": 2, "mean": 4, "max": 8}
        >>> char_supplier = datacraft.suppliers.list_stats_sampler("#!@#$%^&*()_-~", min=2, mean=4, max=8)
        >>> two_to_eight_chars = char_supplier.next(0)
    """
    return list_stats_sampler_supplier(data, **kwargs)


def list_count_sampler(data: list, **kwargs) -> ValueSupplierInterface:
    """
    Samples N elements from data list based on config.  If count is provided,
    each iteration exactly count elements will be returned.  If only min is provided,
    between min and the total number of elements will be provided. If only max is provided,
    between one and max elements will be returned. Specifying both min and max will provide
    a sample containing a number of elements in this range.


    Args:
        data: list to select subset from

    Keyword Args:
        count: number of elements in list to use
        count_dist: count distribution to use
        min: minimum number of values to return
        max: maximum number of values to return
        join_with: value to join values with, default is None

    Returns:
        the supplier

    Examples:
        >>> import datacraft
        >>> pet_list = ["dog", "cat", "hamster", "pig", "rabbit", "horse"]
        >>> pet_supplier = datacraft.suppliers.list_count_sampler(pet_list, min=2, max=5)
        >>> pet_supplier.next(0)
        ['rabbit', 'cat', 'pig', 'cat']
        >>> pet_supplier = datacraft.suppliers.list_count_sampler(pet_list, count_dist="normal(mean=2,stddev=1,min=1,max=3)")
        >>> pet_supplier.next(0)
        ['pig', 'horse']
    """
    if 'count' in kwargs or 'count_dist' in kwargs:
        counts = count_supplier(**kwargs)
    else:
        min_cnt = int(kwargs.get('min', 1))
        max_cnt = int(kwargs.get('max', len(data))) + 1
        count_range = list(range(min_cnt, max_cnt))
        counts = list_values(count_range, sample=True)
    return ListCountSamplerSupplier(data, counts, kwargs.get('join_with', None))


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
    return buffered(wrapped)


def decorated(supplier: ValueSupplierInterface, **kwargs) -> ValueSupplierInterface:
    """
    Creates a decorated supplier around the provided one

    Args:
        supplier: the supplier to alter
        **kwargs

    Keyword Args:
        prefix (str): prefix to prepend to value, default is ''
        suffix (str): suffix to append to value, default is ''
        quote (str): string to both append and prepend to value, default is ''

    Returns:
        the decorated supplier

    Examples:
        >>> import datacraft
        >>> nums = datacraft.suppliers.values([1, 2, 3, 4, 5])
        >>> prefix_supplier = datacraft.suppliers.decorated(nums, prefix='you are number ')
        >>> prefix_supplier.next(0)
        you are number 1
        >>> suffix_supplier = datacraft.suppliers.decorated(nums, suffix=' more minutes')
        >>> suffix_supplier.next(0)
        1 more minutes
        >>> quoted_supplier = datacraft.suppliers.decorated(nums, quote='"')
        >>> quoted_supplier.next(0)
        "1"
    """
    return DecoratedSupplier(supplier, **kwargs)


def cast(supplier: ValueSupplierInterface, cast_to: str) -> ValueSupplierInterface:
    """
    Provides a cast supplier from explicit cast

    Args:
        supplier: to cast results of
        cast_to: type to cast values to

    Returns:
        the casting supplier
    """
    caster = casters.get(cast_to)
    return CastingSupplier(supplier, caster)


def buffered(wrapped: ValueSupplierInterface, **kwargs) -> ValueSupplierInterface:
    """
    Creates a Value Supplier that buffers the results of the wrapped supplier allowing the retrieval

    Args:
        wrapped: the Value Supplier to buffer values for

    Keyword Args:
        buffer_size: number of produced values to buffer

    Returns:
        a buffered value supplier
    """
    buffer_size = int(kwargs.get('buffer_size', 10))
    return BufferedValueSupplier(wrapped, buffer_size)


def calculate(suppliers_map: Dict[str, ValueSupplierInterface], formula: str) -> ValueSupplierInterface:
    """
    Creates a calculate supplier

    Args:
        suppliers_map: map of name to supplier of values for that name
        formula: to evaluate, should reference keys in suppliers_map

    Returns:
        supplier with calculated values
    """
    engine = template_engines.string(formula)
    return calculate_supplier(suppliers=suppliers_map, engine=engine)


def character_class(data, **kwargs):
    """
    Creates a character class supplier for the given data

    Args:
        data: set of characters to supply as values

    Keyword Args:
        join_with (str): string to join characters with, default is ''
        exclude (str): set of characters to exclude from returned values
        mean (float): mean number of characters to produce
        stddev (float): standard deviation from the mean
        count (int): number of elements in list to use
        count_dist (str): count distribution to use
        min (int): minimum number of characters to return
        max (int): maximum number of characters to return

    Returns:
        supplier for characters
    """
    if 'exclude' in kwargs:
        for char_to_exclude in kwargs.get('exclude'):
            data = data.replace(char_to_exclude, '')
    if utils.any_key_exists(kwargs, ['mean', 'stddev']):
        return list_stats_sampler(data, **kwargs)
    return list_count_sampler(data, **kwargs)


def csv(csv_path, **kwargs):
    """
    Creates a csv supplier

    Args:
        csv_path: path to csv file to supply data from

    Keyword Args:
        column (int): 1 based column number, default is 1
        sample (bool): if the values for the column should be sampled, if supported
        count: constant, list, or weighted map
        count_dist: distribution in named param function style format
        delimiter (str): how items are separated, default is ','
        quotechar (str): string used to quote values, default is '"'
        headers (bool): if the CSV file has a header row
        sample_rows (bool): if sampling should happen at a row level, not valid if buffering is set to true

    Returns:
        supplier for csv field
    """
    field_name = kwargs.get('column', 1)
    sample = utils.is_affirmative('sample', kwargs)
    counts = count_supplier(**kwargs)

    csv_data = _load_csv_data(csv_path, **kwargs)
    return csv_supplier(field_name, csv_data, counts, sample)


_ONE_MB = 1024 * 1024
_SMALL_ENOUGH_THRESHOLD = 250 * _ONE_MB


def _load_csv_data(csv_path, **kwargs):
    """
    Creates the CsvData object, caches the object by file path so that we can share this object across fields

    Args:
        csv_path: path to csv file

    Keyword Args:
        delimiter (str): how items are separated, default is ','
        quotechar (str): string used to quote values, default is '"'
        headers (bool): if the CSV file has a header row
        sample_rows (bool): if sampling should happen at a row level, not valid if buffering is set to true

    Returns:
        the configured CsvData object
    """
    delimiter = kwargs.get('delimiter', ',')
    # in case tab came in as string
    if delimiter == '\\t':
        delimiter = '\t'
    quotechar = kwargs.get('quotechar', '"')
    has_headers = utils.is_affirmative('headers', kwargs)

    size_in_bytes = os.stat(csv_path).st_size
    max_csv_size = int(registries.get_default('large_csv_size_mb')) * _ONE_MB
    sample_rows = utils.is_affirmative('sample_rows', kwargs)
    buffer = size_in_bytes <= max_csv_size
    return load_csv_data(csv_path, delimiter, has_headers, quotechar, sample_rows, buffer)


def date(**kwargs) -> ValueSupplierInterface:
    """
    Creates supplier the provides date values according to specified format and ranges

    Can use one of center_date or (start, end, offset, duration_days) etc.

    Args:
        **kwargs:

    Keyword Args:
        format (str): Format string for dates
        center_date (str): Date matching format to center dates around
        stddev_days (float): Standard deviation in days from center date
        start (str): start date string
        end (str): end date string
        offset (int): number of days to shift the duration, positive is back negative is forward
        duration_days (int): number of days after start, default is 30

    Returns:
        supplier for dates
    """
    hour_supplier = kwargs.pop('hour_supplier')
    if 'center_date' in kwargs or 'stddev_days' in kwargs:
        return _create_stats_based_date_supplier(hour_supplier, **kwargs)
    return _create_uniform_date_supplier(hour_supplier, **kwargs)


def epoch_date(as_millis: bool = False, **kwargs) -> ValueSupplierInterface:
    """
    Creates supplier the provides epoch dates

    Can use one of center_date or (start, end, offset, duration_days) etc.

    Args:
        as_millis: if the timestamp should be millis since epoch, default is seconds

    Keyword Args:
        format (str): Format string for date args used, required if any provided
        center_date (str): Date matching format to center dates around
        stddev_days (float): Standard deviation in days from center date
        start (str): start date string
        end (str): end date string
        offset (int): number of days to shift the duration, positive is back negative is forward
        duration_days (str): number of days after start, default is 30

    Returns:
        supplier for dates
    """
    if 'center_date' in kwargs or 'stddev_days' in kwargs:
        timestamp_distribution, _ = _gauss_date_timestamp(**kwargs)
    else:
        timestamp_distribution, _ = _uniform_date_timestamp(**kwargs)
    return epoch_date_supplier(timestamp_distribution, is_millis=as_millis)


def _create_stats_based_date_supplier(hour_supplier: ValueSupplierInterface, **kwargs):
    """ creates stats based date supplier from config """
    timestamp_distribution, date_format = _gauss_date_timestamp(**kwargs)
    return date_supplier(date_format, timestamp_distribution, hour_supplier)


def _create_uniform_date_supplier(hour_supplier: ValueSupplierInterface, **kwargs):
    """ creates uniform based date supplier from config """
    timestamp_distribution, date_format = _uniform_date_timestamp(**kwargs)
    return date_supplier(date_format, timestamp_distribution, hour_supplier)


def _uniform_date_timestamp(**kwargs):
    duration_days = kwargs.get('duration_days', registries.get_default('date_duration_days'))
    offset = int(kwargs.get('offset', 0))
    start = kwargs.get('start')
    end = kwargs.get('end')
    date_format = kwargs.get('format', registries.get_default('date_format'))
    start_ts, end_ts = uniform_date_timestamp(start, end, offset, duration_days, date_format)  # type: ignore
    if start_ts is None or end_ts is None:
        raise SpecException(f'Unable to generate timestamp supplier from config: {json.dumps(kwargs)}')
    timestamp_distribution = distributions.uniform(start=start_ts, end=end_ts)
    return timestamp_distribution, date_format


_SECONDS_IN_DAY = 24.0 * 60.0 * 60.0


def _gauss_date_timestamp(**kwargs):
    """
    Creates a normally distributed date distribution around the center date

    Keyword Args:
        center_date_str: center date for distribution
        stddev_days: standard deviation from center date in days
        format: format for returned dates

    Returns:
        Distribution that gives normally distributed seconds since epoch for the given params, and date_format_string
    """
    center_date_str = kwargs.get('center_date')
    stddev_days = float(kwargs.get('stddev_days', registries.get_default('date_stddev_days')))
    date_format_string = kwargs.get('format', registries.get_default('date_format'))
    if center_date_str:
        center_date = datetime.datetime.strptime(center_date_str, date_format_string)
    else:
        center_date = datetime.datetime.now()
    mean = center_date.timestamp()
    stddev = stddev_days * _SECONDS_IN_DAY
    return distributions.normal(mean=mean, stddev=stddev), date_format_string


def geo_lat(**kwargs) -> ValueSupplierInterface:
    """
    configures geo latitude type

    Keyword Args:
        precision (int): number of digits after decimal place
        start_lat (int): minimum value for latitude
        end_lat (int): maximum value for latitude
        bbox (list): list of size 4 with format: [min Longitude, min Latitude, max Longitude,  max Latitude]

    Returns:
        supplier for geo.lat type
    """
    return _configure_geo_type(-90.0, 90.0, '_lat', **kwargs)


def geo_long(**kwargs) -> ValueSupplierInterface:
    """
    configures geo longitude type

    Keyword Args:
        precision (int): number of digits after decimal place
        start_long (int): minimum value for longitude
        end_long (int): maximum value for longitude
        bbox (list): list of size 4 with format: [min Longitude, min Latitude, max Longitude,  max Latitude]

    Returns:
        supplier for geo.long type
    """
    return _configure_geo_type(-90.0, 90.0, '_long', **kwargs)


def geo_pair(**kwargs):
    """
    Creates geo pair supplier

    Keyword Args:
        precision (int): number of digits after decimal place
        lat_first (bool): if latitude should be populated before longitude
        start_lat (int): minimum value for latitude
        end_lat (int): maximum value for latitude
        start_long (int): minimum value for longitude
        end_long (int): maximum value for longitude
        bbox (list): list of size 4 with format: [min Longitude, min Latitude, max Longitude,  max Latitude]
        as_list (bool): if the values should be returned as a list
        join_with (str): if the values should be joined with the provided string

    Returns:
        supplier for geo.pair type
    """
    long_supplier = geo_long(**kwargs)
    lat_supplier = geo_lat(**kwargs)
    join_with = kwargs.get('join_with', registries.get_default('geo_join_with'))
    as_list = utils.is_affirmative('as_list', kwargs, registries.get_default('geo_as_list'))
    lat_first = utils.is_affirmative('lat_first', kwargs, registries.get_default('geo_lat_first'))
    combine_config = {
        'join_with': join_with,
        'as_list': as_list
    }
    if lat_first:
        return combine([lat_supplier, long_supplier], **combine_config)
    return combine([long_supplier, lat_supplier], **combine_config)


def _configure_geo_type(default_start, default_end, suffix, **kwargs):
    precision = kwargs.get('precision', registries.get_default('geo_precision'))
    if not str(precision).isnumeric():
        raise SpecException(f'precision for geo should be valid integer >= 0: {json.dumps(kwargs)}')
    start, end = _get_start_end(default_start, default_end, suffix, **kwargs)
    return random_range(start, end, precision)


def _get_start_end(default_start, default_end, suffix, **kwargs):
    """ determines the valid range, changes if bbox in config """
    if 'bbox' in kwargs:
        bbox = kwargs['bbox']
        if not isinstance(bbox, list) or len(bbox) != 4:
            raise SpecException(
                'Bounding box must be list of size 4 with format: [min Longitude, min Latitude, max Longitude, '
                'max Latitude]')
        if 'lat' in suffix:
            default_start = bbox[1]
            default_end = bbox[3]
        else:
            default_start = bbox[0]
            default_end = bbox[2]
    # start_lat or start_long overrides bbox or defaults
    start = kwargs.get('start' + suffix, default_start)
    # end_lat or end_long overrides bbox or defaults
    end = kwargs.get('end' + suffix, default_end)
    return start, end


def ip_supplier(**kwargs) -> ValueSupplierInterface:
    """
    Creates a value supplier for ipv v4 addresses

    Keyword Args:
        base (str): base of ip address, i.e. "192", "10." "100.100", "192.168.", "10.10.10"
        cidr (str): cidr to use only one /8 /16 or /24, i.e. "192.168.0.0/24", "10.0.0.0/16", "100.0.0.0/8"

    Returns:
        supplier for ip addresses

    Raises:
        SpecException if one of base or cidr is not provided

    Examples:
        >>> import datacraft
        >>> ips = datacraft.suppliers.ip_supplier(base="192.168.1")
        >>> ips.next(0)
        '192.168.1.144'
    """
    if 'base' in kwargs and 'cidr' in kwargs:
        raise SpecException('Must supply only one of base or cidr param: ' + json.dumps(kwargs))

    parts = _get_base_parts(kwargs)
    # this is the same thing as a constant
    if len(parts) == 4:
        return values('.'.join(parts))
    sample = kwargs.get('sample', 'yes')
    octet_supplier_map = {
        'first': _create_octet_supplier(parts, 0, sample),
        'second': _create_octet_supplier(parts, 1, sample),
        'third': _create_octet_supplier(parts, 2, sample),
        'fourth': _create_octet_supplier(parts, 3, sample),
    }
    return network.ipv4(octet_supplier_map)


def _get_base_parts(config):
    """
    Builds the base ip array for the first N octets based on
    supplied base or on the /N subnet mask in the cidr
    """
    if 'base' in config:
        parts = config.get('base').split('.')
    else:
        parts = []

    if 'cidr' in config:
        cidr = config['cidr']
        mask = _validate_and_extract_mask(cidr)
        ip_parts = cidr[0:cidr.index('/')].split('.')
        if len(ip_parts) < 4 or not all(part.isdigit() for part in ip_parts):
            raise ValueError('Invalid IP in cidr for config: ' + json.dumps(config))
        if mask == '8':
            parts = ip_parts[0:1]
        elif mask == '16':
            parts = ip_parts[0:2]
        elif mask == '24':
            parts = ip_parts[0:3]
    return parts


def _validate_and_extract_mask(cidr):
    """ validates the cidr is on that can be used for ip type """
    if '/' not in cidr:
        raise ValueError(f'Invalid Subnet Mask in cidr: {cidr}, only one of /8 /16 or /24 supported')
    mask = cidr[cidr.index('/') + 1:]
    if not mask.isdigit() or int(mask) not in [8, 16, 24]:
        raise ValueError(f'Invalid Subnet Mask in cidr: {cidr}, only one of /8 /16 or /24 supported')
    return mask


def _create_octet_supplier(parts, index, sample):
    """ creates a value supplier for the index'th octet """
    # this index is for a part that is static, create a single value supplier for that part
    if len(parts) >= index + 1 and parts[index].strip() != '':
        octet = parts[index].strip()
        if not octet.isdigit():
            raise ValueError(f'Octet: {octet} invalid for base, Invalid Input: ' + '.'.join(parts))
        if not 0 <= int(octet) <= 255:
            raise ValueError(
                f'Each octet: {octet} must be in range of 0 to 255, Invalid Input: ' + '.'.join(parts))
        return values(octet)
    # need octet range at this point
    octet_range = list(range(0, 255))
    return values(octet_range, sample=sample)


def ip_precise(cidr: str, sample: bool = False) -> ValueSupplierInterface:
    """Creates a value supplier that produces precise ip address from the given cidr

    Args:
        cidr: notation specifying ip range
        sample: if the ip addresses should be sampled from the available set

    Returns:
        supplier for precise ip addresses

    Examples:
        >>> import datacraft
        >>> ips = datacraft.suppliers.ip_precise(cidr="192.168.0.0/22", sample=False)
        >>> ips.next(0)
        '192.168.0.0'
        >>> ips.next(1)
        '192.168.0.1'
        >>> ips = datacraft.suppliers.ip_precise(cidr="192.168.0.0/22", sample=True)
        >>> ips.next(0)
        '192.168.0.127'
        >>> ips.next(1)
        '192.168.0.196'
    """
    return network.ip_precise(cidr, sample)


def mac_address(delimiter: Union[str, None] = None) -> ValueSupplierInterface:
    """Creates a value supplier that produces mac addresses

    Args:
        delimiter: how mac address pieces are separated, default is ':'

    Returns:
        supplier for mac addresses

    Examples:
        >>> import datacraft
        >>> macs = datacraft.suppliers.mac_address()
        >>> macs.next(0)
        '1E:D4:0F:59:41:FA'
        >>> macs = datacraft.suppliers.mac_address('-')
        >>> macs.next(0)
        '4D-93-36-59-BD-09'
    """
    if delimiter is None:
        delimiter = registries.get_default('mac_addr_separator')
    return network.mac_address(delimiter)


def combine(to_combine, join_with: Union[str, None] = None, as_list: Union[bool, None] = None):
    """Creates a value supplier that will combine the outputs of the provided suppliers in order. The default is to
    join the values with an empty string. Provide the join_with config param to specify a different string to
    join the values with. Set as_list to true, if the values should be returned as a list and not joined

    Args:
        to_combine: list of suppliers to combine in order of combination
        as_list: if the results should be returned as a list
        join_with: value to use to join the values

    Returns:
        supplier for mac addresses

    Examples:
        >>> import datacraft
        >>> pet_supplier = datacraft.suppliers.values(["dog", "cat", "hamster", "pig", "rabbit", "horse"], sample=True)
        >>> job_supplier = datacraft.suppliers.values(["breeder", "trainer", "fighter", "wrestler"], sample=True)
        >>> interesting_jobs = datacraft.suppliers.combine([pet_supplier, job_supplier], join_with=' ')
        >>> next_career = interesting_jobs.next(0)
        >>> next_career
        'pig wrestler'
    Returns:

    """
    if as_list is None:
        as_list = registries.get_default('combine_as_list')
    if join_with is None:
        join_with = registries.get_default('combine_join_with')
    return combine_supplier(to_combine, join_with, as_list)


def uuid(variant: Union[int, None] = None) -> ValueSupplierInterface:
    """
    Creates a UUid Value Supplier

    Args:
        variant: of uuid to use, default is 4

    Returns:
        supplier to supply uuids with
    """
    if variant is None:
        variant = registries.get_default('uuid_variant')

    if variant not in [1, 3, 4, 5]:
        raise ValueError(f'Invalid variant {variant}')
    return uuid_supplier(variant)


def range_supplier(start: Union[int, float],
                   end: Union[int, float],
                   step: Union[int, float] = 1,
                   **kwargs):
    """
    Creates a Value Supplier for given range of data

    Args:
        start: start of range
        end: end of range
        step: of range values

    Keyword Args:
        precision (int): Number of decimal places to use, in case of floating point range

    Returns:
        supplier to supply ranges of values with
    """
    if utils.any_is_float([start, end, step]):
        range_values_gen = ranges.float_range(float(start), float(end), float(step), kwargs.get("precision"))
        return resettable(range_values_gen)
    return ranges.range_wrapped(range(start, end, step))  # type: ignore


def resettable(iterator: ResettableIterator):
    """Wraps a ResettableIterator to supply values from

    Args:
        iterator: iterator with reset() method

    Returns:
        supplier to supply generated values with
    """
    return iter_supplier(iterator)


def sample(data: list, **kwargs):
    """Creates a supplier that selects elements from the data list based on the supplier kwargs

    Args:
        data: list of data values to supply values from

    Keyword Args:
        mean (float): mean number of values to include in list
        stddev (float): standard deviation from the mean
        count: number of elements in list to use
        count_dist: count distribution to use
        min: minimum number of values to return
        max: maximum number of values to return
        join_with: value to join values with, default is None

    Returns:
        supplier to supply subsets of data list

    Examples:
        >>> import datacraft
        >>> supplier = datacraft.suppliers.sample(['dog', 'cat', 'rat'], mean=2)
        >>> supplier.next(1)
        ['cat', 'rat']
    """
    if utils.any_key_exists(kwargs, ['mean', 'stddev']):
        return list_stats_sampler(data, **kwargs)
    return list_count_sampler(data, **kwargs)


def unicode_range(data, **kwargs):
    """Creates a unicode supplier for single or multiple unicode ranges

    Args:
        data: list of unicode ranges to sample from

    Keyword Args:
        mean (float): mean number of values to produce
        stddev (float): standard deviation from the mean
        count (int): number of unicode characters to produce
        count_dist (str): count distribution to use
        min (int): minimum number of characters to return
        max (int): maximum number of characters to return
        as_list (bool): if the results should be returned as a list
        join_with (str): value to join values with, default is ''

    Returns:
        supplier to supply subsets of data list
    """
    if isinstance(data[0], list):
        suppliers_list = [_single_unicode_range(sublist, **kwargs) for sublist in data]
        return from_list_of_suppliers(suppliers_list, True)
    return _single_unicode_range(data, **kwargs)


def _single_unicode_range(data, **kwargs):
    # supplies range of data as floats
    range_data = list(range(utils.decode_num(data[0]), utils.decode_num(data[1]) + 1))
    # casts the floats to ints
    if utils.any_key_exists(kwargs, ['mean', 'stddev']):
        if 'as_list' not in kwargs:
            kwargs['as_list'] = 'true'
        wrapped = list_stats_sampler(range_data, **kwargs)
    else:
        wrapped = list_count_sampler(range_data, **kwargs)
    return unicode_range_supplier(wrapped)


def templated(supplier_map: Dict[str, ValueSupplierInterface],
              template_str) -> ValueSupplierInterface:
    """
    Creates a supplier that populates the template string from the supplier map

    Args:
        supplier_map: map of field name -> value supplier for it
        template_str: templated string to populate

    Returns:
        value supplier for template

    Examples:
        >>> from datacraft import suppliers
        >>> char_to_num_supplier = { 'char': suppliers.values(['a', 'b', 'c']), 'num': suppliers.values([1, 2, 3]) }
        >>> letter_number_template = 'letter {{ char }}, number {{ num }}'
        >>> supplier = suppliers.templated(char_to_num_supplier, letter_number_template)
        >>> supplier.next(0)
        'letter a, nummber 1'
    """
    engine = template_engines.string(template_str)
    return templated_supplier(supplier_map, engine)


def cut(supplier: datacraft.ValueSupplierInterface,
        start: int = 0,
        end: Union[int, None] = None):
    """Trim output of given supplier from start to end, if length permits

    Args:
        supplier: to get output from
        start: where in output string to cut from (inclusive)
        end: where to end cut (exclusive)

    Returns:
        The shortened version of the output string
    """
    return cut_supplier(supplier, start, end)
