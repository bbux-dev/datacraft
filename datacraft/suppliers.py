"""
Factory like module for core supplier related functions.
"""
import datetime
import os
import json
import logging
from typing import Union, List, Dict, Any

from . import registries, casters, distributions, utils, template_engines
from .exceptions import SpecException
from .supplier.common import (SingleValue, MultipleValueSupplier, RotatingSupplierList, DecoratedSupplier,
                              CastingSupplier, RandomRangeSupplier, DistributionBackedSupplier,
                              BufferedValueSupplier, ListCountSamplerSupplier,
                              list_stats_sampler, list_value_supplier, weighted_values_explicit)
from .supplier.combine import combine_supplier
from .supplier.calculate import calculate_supplier
from .supplier.date import date_supplier
from .supplier.model import Distribution, ValueSupplierInterface
from .supplier.csv import load_csv_data, csv_supplier

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
        >>> import datacraft
        >>> spec = {"type": "values", "data": [1,2,3,5,8,13]}
        >>> fib_supplier = datacraft.suppliers.values(spec)
        >>> fib_supplier = datacraft.suppliers.values([1,2,3,5,8,13])
        >>> weights =  {"1": 0.1, "2": 0.2, "3": 0.1, "4": 0.2, "5": 0.1, "6": 0.2, "7": 0.1}
        >>> mostly_even_supplier = datacraft.suppliers.values(weights)
    """
    # shortcut notations no type, or data, the spec is the data
    if _data_not_in_spec(spec):
        data = spec
    else:
        data = spec['data']

    config = utils.load_config(spec, loader, **kwargs)
    do_sampling = utils.is_affirmative('sample', config, default=registries.get_default('sample_mode'))

    if isinstance(data, list):
        # this supplier can handle the count param itself, so just return it
        return _value_list(data, config, do_sampling)
    if isinstance(data, dict):
        supplier = weighted_values(data)
    else:
        supplier = constant(data)

    # Check for count param
    if 'count' in config or 'count_dist' in config:
        return MultipleValueSupplier(supplier, count_supplier(**config))
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
        count_dist: distribution in named param function style format

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
        supplier = _value_list(data, None, False)
    elif isinstance(data, dict):
        supplier = weighted_values(data)
    elif isinstance(data, Distribution):
        supplier = cast(distribution_supplier(data), cast_to='int')
    else:
        try:
            supplier = constant(int(data))
        except ValueError as value_error:
            raise SpecException(f'Invalid count param: {data}') from value_error

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


def enhance(supplier, **kwargs):
    """

    Args:
        supplier: to enhance if configured to do so

    Keyword Args:
        cast (str): caster to apply
        prefix (str): prefix to prepend to value, default is ''
        suffix (str): suffix to append to value, default is ''
        quote (str): string to both append and prepend to value, default is ''


    Returns:

    """
    if _is_cast(**kwargs):
        supplier = cast(supplier, cast_to=kwargs.get('cast'))
    if _is_decorated(**kwargs):
        supplier = decorated(supplier, **kwargs)
    if _is_buffered(**kwargs):
        supplier = buffered(supplier, **kwargs)
    return supplier


def _is_decorated(**kwargs) -> bool:
    """ is this spec a decorated one """
    return any(key in kwargs for key in ['prefix' ,'suffix' ,'quote'])


def _is_cast(**kwargs) -> bool:
    """ Does this spec requires casting """
    return 'cast' in kwargs


def _is_buffered(**kwargs) -> bool:
    """ Should the values for this spec be buffered """
    return 'buffer_size' in kwargs or utils.is_affirmative('buffer', kwargs)


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
    return list_value_supplier(data, count_supplier(**config), do_sampling, as_list)


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
        >>> import datacraft
        >>> weights = {"dog": 0.5, "cat": 0.2, "bunny": 0.1, "hamster": 0.1, "pig": 0.05, "snake": 0.04, "rat": 0.01}
        >>> weighted_pet_supplier = datacraft.suppliers.weighted_values(weights)
        >>> most_likely_a_dog = weighted_pet_supplier.next(0)
    """
    if len(data) == 0:
        raise SpecException('Invalid Weights, no values defined')
    if config is None:
        config = {}
    choices = list(data.keys())
    weights = list(data.values())
    if not isinstance(weights[0], float):
        raise SpecException('Invalid type for weights: ' + str(type(weights[0])))
    return weighted_values_explicit(choices, weights, count_supplier(**config))


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
        >>> import datacraft
        >>> pet_supplier = datacraft.suppliers.values(["dog", "cat", "hamster", "pig", "rabbit", "horse"], sample=True)
        >>> job_supplier = datacraft.suppliers.values(["breeder", "trainer", "fighter", "wrestler"], sample=True)
        >>> interesting_jobs = datacraft.suppliers.combine([pet_supplier, job_supplier], {'join_with': ' '})
        >>> next_career = interesting_jobs.next(0)
    """
    if config is None:
        config = {}
    as_list = utils.is_affirmative('as_list', config)
    join_with = config.get('join_with', registries.get_default('combine_join_with'))
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
        >>> range_supplier = datacraft.suppliers.random_range(5, 25, precision=3)
        >>> # should be between 5 and 25 with 3 decimal places
        >>> next_value = range_supplier.next(0))
    """
    return RandomRangeSupplier(start, end, precision, count_supplier(data=count))


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
        >>> import datacraft
        >>> stats_config = {"mean": 2, "stddev": 1}
        >>> pet_list = ["dog", "cat", "hamster", "pig", "rabbit", "horse"]
        >>> pet_supplier = datacraft.suppliers.list_stat_sampler(pet_list, stats_config)
        >>> new_pets = pet_supplier.next(0)

        >>> char_config = {"min": 2, "mean": 4, "max": 8}
        >>> char_supplier = datacraft.suppliers.list_stat_sampler("#!@#$%^&*()_-~", char_config)
        >>> two_to_eight_chars = char_supplier.next(0)
    """
    config['as_list'] = utils.is_affirmative('as_list', config, False)
    return list_stats_sampler(data, **config)


def list_count_sampler(data: list, **kwargs) -> ValueSupplierInterface:
    """
    Samples N elements from data list based on config.  If count is provided,
    each iteration exactly count elements will be returned.  If only min is provided,
    between min and the total number of elements will be provided. If only max is provided,
    between one and max elements will be returned. Specifying both min and max will provide
    a sample containing a number of elements in this range.


    Args:
        data: list to select subset from
        **kwargs:

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
        >>> new_pets = pet_supplier.next(0)
        >>> pet_supplier = datacraft.suppliers.list_count_sampler(pet_list, count_dist="normal(mean=2,min=1,max=3)")
        >>> new_pets = pet_supplier.next(0)
    """
    if 'count' in kwargs or 'count_dist' in kwargs:
        counts = count_supplier(**kwargs)
    else:
        min_cnt = int(kwargs.get('min', 1))
        max_cnt = int(kwargs.get('max', len(data))) + 1
        count_range = list(range(min_cnt, max_cnt))
        counts = _value_list(count_range, None, True)
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
        supplier: the supplier to enhance
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
        >>> supplier = datacraft.suppliers.decorated(nums, prefix='you are number ')
        >>> supplier.next(0)
        you are number 1
        >>> supplier = datacraft.suppliers.decorated(nums, suffix=' more minutes')
        >>> supplier.next(0)
        1 more minutes
        >>> supplier = datacraft.suppliers.decorated(nums, quote='"')
        >>> supplier.next(0)
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
        ValueSupplierInterface with calculated values
    """
    engine = template_engines.string(formula)
    return calculate_supplier(suppliers=suppliers_map, engine=engine)


def character_class(data, **kwargs):
    """
    Creates a character class supplier for the given data

    Args:
        data: set of characters to supply as values
        **kwargs:

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
        ValueSupplierInterface for characters
    """
    if 'exclude' in kwargs:
        for char_to_exclude in kwargs.get('exclude'):
            data = data.replace(char_to_exclude, '')
    if utils.any_key_exists(kwargs, ['mean', 'stddev']):
        return list_stat_sampler(data, kwargs)
    return list_count_sampler(data, **kwargs)


def csv(csv_path, **kwargs):
    """
    Creates a csv supplier

    Args:
        csv_path: path to csv file to supply data from
        **kwargs:

    Keyword Args:

    Returns:
        ValueSupplierInterface for csv field
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
        duration_days (str): number of days after start, default is 30
        date_format_string (str): format for parsing dates

    Returns:
        ValueSupplierInterface for dates
    """
    hour_supplier = kwargs.pop('hour_supplier')
    if 'center_date' in kwargs or 'stddev_days' in kwargs:
        return _create_stats_based_date_supplier(hour_supplier, **kwargs)
    return _create_uniform_date_supplier(hour_supplier, **kwargs)


def _create_stats_based_date_supplier(hour_supplier: ValueSupplierInterface, **kwargs):
    """ creates stats based date supplier from config """
    center_date = kwargs.get('center_date')
    stddev_days = kwargs.get('stddev_days', registries.get_default('date_stddev_days'))
    date_format = kwargs.get('format', registries.get_default('date_format'))
    timestamp_distribution = gauss_date_timestamp(center_date, float(stddev_days), date_format)
    return date_supplier(date_format, timestamp_distribution, hour_supplier)


def _create_uniform_date_supplier(hour_supplier: ValueSupplierInterface, **kwargs):
    """ creates uniform based date supplier from config """
    duration_days = kwargs.get('duration_days', registries.get_default('date_duration_days'))
    offset = int(kwargs.get('offset', 0))
    start = kwargs.get('start')
    end = kwargs.get('end')
    date_format = kwargs.get('format', registries.get_default('date_format'))
    timestamp_distribution = uniform_date_timestamp(start, end, offset, duration_days, date_format)  # type: ignore
    if timestamp_distribution is None:
        raise SpecException(f'Unable to generate timestamp supplier from config: {json.dumps(kwargs)}')
    return date_supplier(date_format, timestamp_distribution, hour_supplier)


def uniform_date_timestamp(
        start: str,
        end: str,
        offset: int,
        duration: int,
        date_format_string: str) -> Union[None, Distribution]:
    """
    Creates a uniform distribution for the start and end dates shifted by the offset

    Args:
        start: start date string
        end: end date string
        offset: number of days to shift the duration, positive is back negative is forward
        duration: number of days after start
        date_format_string: format for parsing dates

    Returns:
        Distribution that gives uniform seconds since epoch for the given params
    """
    offset_date = datetime.timedelta(days=offset)
    if start:
        try:
            start_date = datetime.datetime.strptime(start, date_format_string) - offset_date
        except TypeError as err:
            raise SpecException(f"TypeError. Format: {date_format_string}, may not match param: {start}") from err
    else:
        start_date = datetime.datetime.now() - offset_date
    if end:
        # buffer end date by one to keep inclusive
        try:
            end_date = datetime.datetime.strptime(end, date_format_string) \
                       + datetime.timedelta(days=1) - offset_date
        except TypeError as err:
            raise SpecException(f"TypeError. Format: {date_format_string}, may not match param: {end}") from err
    else:
        # start date already include offset, don't include it here
        end_date = start_date + datetime.timedelta(days=abs(int(duration)), seconds=1)

    start_ts = int(start_date.timestamp())
    end_ts = int(end_date.timestamp())
    if end_ts < start_ts:
        _log.warning("End date (%s) is before start date (%s)", start_date, end_date)
        return None
    return distributions.uniform(start=start_ts, end=end_ts)


_SECONDS_IN_DAY = 24.0 * 60.0 * 60.0


def gauss_date_timestamp(
        center_date_str: Union[str, None],
        stddev_days: float,
        date_format_string: str):
    """
    Creates a normally distributed date distribution around the center date

    Args:
        center_date_str: center date for distribution
        stddev_days: standard deviation from center date in days
        date_format_string: format for returned dates

    Returns:
        Distribution that gives normally distributed seconds since epoch for the given params
    """
    if center_date_str:
        center_date = datetime.datetime.strptime(center_date_str, date_format_string)
    else:
        center_date = datetime.datetime.now()
    mean = center_date.timestamp()
    stddev = stddev_days * _SECONDS_IN_DAY
    return distributions.normal(mean=mean, stddev=stddev)


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
        return combine([lat_supplier, long_supplier], combine_config)
    return combine([long_supplier, lat_supplier], combine_config)


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
