"""
Internal module where the build in types are registered and configured
"""
import csv
import datetime
import decimal
import json
import logging
import math
import os
import string
from typing import Union, Dict

from . import distributions, suppliers, registries, template_engines, schemas, utils
from .exceptions import SpecException
from .loader import Loader
from .supplier import key_suppliers
# for calculate
from .supplier.calculate import calculate_supplier
# for combine
from .supplier.combine import combine_supplier
from .supplier.common import weighted_values_explicit
# for csv
from .supplier.csv import CsvData, load_csv_data, csv_supplier
# for date
from .supplier.date import date_supplier
from .supplier.model import Distribution
# for nested
from .supplier.nested import nested_supplier
# for network
from .supplier.network import ipv4, ip_precise, mac_address
# for refs
from .supplier.refs import weighted_ref_supplier
# for unicode ranges
from .supplier.unicode import unicode_range_supplier
# for uuid
from .supplier.uuid import uuid_supplier

##############
# Type Keys
##############
_VALUES_KEY = 'values'
_CALCULATE_KEY = 'calculate'
_CHAR_CLASS_KEY = 'char_class'
_DATE_KEY = 'date'
_DATE_ISO_KEY = 'date.iso'
_DATE_ISO_US_KEY = 'date.iso.us'
_GEO_LAT_KEY = 'geo.lat'
_GEO_LONG_KEY = 'geo.long'
_GEO_PAIR_KEY = 'geo.pair'
_COMBINE_KEY = 'combine'
_COMBINE_LIST_KEY = 'combine-list'
_IP_KEY = 'ip'
_IPV4_KEY = 'ipv4'
_IP_PRECISE_KEY = 'ip.precise'
_NET_MAC_KEY = 'net.mac'
_RANGE_KEY = 'range'
_RAND_RANGE_KEY = 'rand_range'
_RAND_INT_RANGE_KEY = 'rand_int_range'
_WEIGHTED_REF_KEY = 'weighted_ref'
_SELECT_LIST_SUBSET_KEY = 'select_list_subset'
_UNICODE_RANGE_KEY = 'unicode_range'
_UUID_KEY = 'uuid'

_log = logging.getLogger('datagen.types')


##############
# values
##############
@registries.registry.schemas(_VALUES_KEY)
def _get_schema():
    """ returns the values schema """
    return schemas.load(_VALUES_KEY)


##############
# calculate
##############
@registries.registry.schemas(_CALCULATE_KEY)
def _calculate_schema():
    """ get the schema for the calculate type """
    return schemas.load(_CALCULATE_KEY)


@registries.registry.types(_CALCULATE_KEY)
def _configure_calculate_supplier(field_spec: dict, loader: Loader):
    """ configures supplier for calculate type """
    if 'refs' not in field_spec and 'fields' not in field_spec:
        raise SpecException('Must define one of fields or refs. %s' % json.dumps(field_spec))
    if 'refs' in field_spec and 'fields' in field_spec:
        raise SpecException('Must define only one of fields or refs. %s' % json.dumps(field_spec))
    template = field_spec.get('formula')
    if template is None:
        raise SpecException('Must define formula for calculate type. %s' % json.dumps(field_spec))

    mappings = _get_mappings(field_spec, 'refs')
    mappings.update(_get_mappings(field_spec, 'fields'))

    if len(mappings) < 1:
        raise SpecException('fields or refs empty: %s' % json.dumps(field_spec))

    suppliers_map = {}
    for field_or_ref, alias in mappings.items():
        supplier = loader.get(field_or_ref)
        suppliers_map[alias] = supplier

    engine = template_engines.string(template)
    return calculate_supplier(suppliers=suppliers_map, engine=engine)


def _get_mappings(field_spec, lookup_key):
    """ retrieve the field aliasing for the given key, refs or fields """
    mappings = field_spec.get(lookup_key, [])
    if isinstance(mappings, list):
        mappings = {_key: _key for _key in mappings}
    return mappings


###############
# char_class
###############
_UNDER_SCORE = '_'

_CLASS_MAPPING = {
    "ascii": ''.join(chr(x) for x in range(128)),
    "lower": string.ascii_lowercase,
    "upper": string.ascii_uppercase,
    "letters": string.ascii_letters,
    "word": f'{string.ascii_letters}{string.digits}{_UNDER_SCORE}',
    "printable": string.printable,
    "visible": ''.join(string.printable.split()),
    "punctuation": string.punctuation,
    "special": string.punctuation,
    "digits": string.digits,
    "hex": string.hexdigits,
    "hex-lower": string.digits + 'abcdef',
    "hex-upper": string.digits + 'ABCDEF',
}


@registries.registry.schemas(_CHAR_CLASS_KEY)
def _get_char_class_schema():
    """ get the schema for the char_class type """
    return schemas.load(_CHAR_CLASS_KEY)


for class_key in _CLASS_MAPPING:
    @registries.registry.schemas("cc-" + class_key)
    def _get_char_class_alias_schema():
        """ get the schema for the char_class type """
        return schemas.load(_CHAR_CLASS_KEY)


@registries.registry.types(_CHAR_CLASS_KEY)
def _configure_char_class_supplier(spec, _):
    """ configure the supplier for char_class types """
    if 'data' not in spec:
        raise SpecException(f'Data is required field for char_class type: {json.dumps(spec)}')
    config = spec.get('config', {})
    data = spec['data']
    if isinstance(data, str) and data in _CLASS_MAPPING:
        data = _CLASS_MAPPING[data]
    if isinstance(data, list):
        new_data = [_CLASS_MAPPING[datum] if datum in _CLASS_MAPPING else datum for datum in data]
        data = ''.join(new_data)
    if 'exclude' in config:
        for char_to_exclude in config.get('exclude'):
            data = data.replace(char_to_exclude, '')
    if 'join_with' not in config:
        config['join_with'] = registries.get_default('char_class_join_with')
    if utils.any_key_exists(config, ['mean', 'stddev']):
        return suppliers.list_stat_sampler(data, config)
    return suppliers.list_count_sampler(data, config)


for class_key in _CLASS_MAPPING   :
    @registries.registry.types("cc-" + class_key)
    def _configure_char_class_alias_supplier(spec, loader):
        """ configure the supplier for char_class alias types """
        spec['data'] = class_key
        return _configure_char_class_supplier(spec, loader)


############
# combine
############
@registries.registry.schemas(_COMBINE_KEY)
def _get_combine_schema():
    """ get the schema for the combine type """
    return schemas.load(_COMBINE_KEY)


@registries.registry.schemas(_COMBINE_LIST_KEY)
def _get_combine_list_schema():
    """ get the schema for the combine_list type """
    return schemas.load(_COMBINE_LIST_KEY)


@registries.registry.types(_COMBINE_KEY)
def _configure_combine_supplier(field_spec, loader):
    """ configures supplier for combine type """
    if 'refs' not in field_spec and 'fields' not in field_spec:
        raise SpecException('Must define one of fields or refs. %s' % json.dumps(field_spec))

    if 'refs' in field_spec:
        supplier = _load_combine_from_refs(field_spec, loader)
    else:
        supplier = _load_combine_from_fields(field_spec, loader)
    return supplier


@registries.registry.types(_COMBINE_LIST_KEY)
def _configure_combine_list_supplier(field_spec, loader):
    """ configures supplier for combine-list type """
    if 'refs' not in field_spec:
        raise SpecException('Must define refs for combine-list type. %s' % json.dumps(field_spec))

    refs_list = field_spec['refs']
    if len(refs_list) < 1 or not isinstance(refs_list[0], list):
        raise SpecException(
            'refs pointer must be list of lists: i.e [["ONE", "TWO"]]. %s' % json.dumps(field_spec))

    suppliers_list = []
    for ref in refs_list:
        spec = dict(field_spec)
        spec['refs'] = ref
        suppliers_list.append(_load_combine_from_refs(spec, loader))
    return suppliers.from_list_of_suppliers(suppliers_list, True)


def _load_combine_from_refs(combine_field_spec, loader):
    """ loads the combine type from a set of refs """
    keys = combine_field_spec.get('refs')
    return _load_combine(combine_field_spec, keys, loader)


def _load_combine_from_fields(combine_field_spec, loader):
    """ load the combine type from a set of field names """
    keys = combine_field_spec.get('fields')
    return _load_combine(combine_field_spec, keys, loader)


def _load_combine(combine_field_spec, keys, loader):
    """ create the combine supplier for the types from the given keys """
    to_combine = []
    for key in keys:
        supplier = loader.get(key)
        to_combine.append(supplier)
    config = combine_field_spec.get('config', {})
    as_list = config.get('as_list', registries.get_default('combine_as_list'))
    joiner = config.get('join_with', registries.get_default('combine_join_with'))
    return combine_supplier(to_combine, as_list, joiner)


############
# config_ref
############
@registries.registry.types('config_ref')
def _config_ref_handler(_, __):
    """" Does nothing, just place holder """


########
# csv
#######
_ONE_MB = 1024 * 1024
_SMALL_ENOUGH_THRESHOLD = 250 * _ONE_MB

# to keep from reloading the same CsvData
_csv_data_cache: Dict[str, CsvData] = {}


@registries.registry.types('csv')
def _configure_csv(field_spec, loader):
    """ Configures the csv value supplier for this field """
    config = utils.load_config(field_spec, loader)

    field_name = config.get('column', 1)
    sample = utils.is_affirmative('sample', config)
    count_supplier = suppliers.count_supplier_from_data(config.get('count', 1))

    csv_data = _load_csv_data(field_spec, config, loader.datadir)
    return csv_supplier(count_supplier, csv_data, field_name, sample)


@registries.registry.schemas('csv')
def _get_csv_schema():
    """ get the schema for the csv type """
    return schemas.load('csv')


@registries.registry.types('weighted_csv')
def _configure_weighted_csv(field_spec, loader):
    """ Configures the weighted_csv value supplier for this field """

    config = utils.load_config(field_spec, loader)

    field_name = config.get('column', 1)
    weight_column = config.get('weight_column', 2)
    count_supplier = suppliers.count_supplier_from_data(config.get('count', 1))

    datafile = config.get('datafile', registries.get_default('csv_file'))
    csv_path = f'{loader.datadir}/{datafile}'
    has_headers = utils.is_affirmative('headers', config)
    numeric_index = isinstance(field_name, int)
    if numeric_index and field_name < 1:
        raise SpecException(f'Invalid index {field_name}, one based indexing used for column numbers')

    if has_headers and not numeric_index:
        choices = _read_named_column(csv_path, field_name)
        weights = _read_named_column_weights(csv_path, weight_column)
    else:
        choices = _read_indexed_column(csv_path, int(field_name), skip_first=numeric_index)
        weights = _read_indexed_column_weights(csv_path, int(weight_column), skip_first=numeric_index)
    return weighted_values_explicit(choices, weights, count_supplier)


@registries.registry.schemas('weighted_csv')
def _get_weighted_csv_schema():
    """ get the schema for the weighted_csv type """
    return schemas.load('weighted_csv')


def _read_named_column(csv_path: str, column_name: str):
    """ reads values from a named column into a list """
    with open(csv_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        return [val[column_name] for val in reader]


def _read_named_column_weights(csv_path: str, column_name: str):
    """ reads values for weights for named column into a list """
    with open(csv_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        return [float(val[column_name]) for val in reader]


def _read_indexed_column(csv_path: str, column_index: int, skip_first: bool):
    """ reads values from a indexed column into a list """
    with open(csv_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        if skip_first:
            next(reader)
        return [val[column_index - 1] for val in reader]


def _read_indexed_column_weights(csv_path: str, column_index: int, skip_first: bool):
    """ reads values for weights for indexed column into a list """
    with open(csv_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        if skip_first:
            next(reader)
        return [float(val[column_index - 1]) for val in reader]


def _load_csv_data(field_spec, config, datadir):
    """
    Creates the CsvData object, caches the object by file path so that we can share this object across fields

    Args:
        field_spec: that triggered the creation
        config: to use to do the creation
        datadir: where to look for data files

    Returns:
        the configured CsvData object
    """
    datafile = config.get('datafile', registries.get_default('csv_file'))
    csv_path = f'{datadir}/{datafile}'
    if csv_path in _csv_data_cache:
        return _csv_data_cache.get(csv_path)

    if not os.path.exists(csv_path):
        raise SpecException(f'Unable to locate data file: {datafile} in data dir: {datadir} for spec: '
                            + json.dumps(field_spec))
    delimiter = config.get('delimiter', ',')
    # in case tab came in as string
    if delimiter == '\\t':
        delimiter = '\t'
    quotechar = config.get('quotechar', '"')
    has_headers = utils.is_affirmative('headers', config)

    size_in_bytes = os.stat(csv_path).st_size
    max_csv_size = int(registries.get_default('large_csv_size_mb')) * _ONE_MB
    sample_rows = utils.is_affirmative('sample_rows', config)
    buffer = size_in_bytes <= max_csv_size
    csv_data = load_csv_data(csv_path, delimiter, has_headers, quotechar, sample_rows, buffer)
    _csv_data_cache[csv_path] = csv_data
    return csv_data


#######
# date
#######
_ISO_FORMAT_NO_MICRO = '%Y-%m-%dT%H:%M:%S'
_ISO_FORMAT_WITH_MICRO = '%Y-%m-%dT%H:%M:%S.%f'

_SECONDS_IN_DAY = 24.0 * 60.0 * 60.0


@registries.registry.schemas(_DATE_KEY)
def _get_date_schema():
    """ returns the schema for date types """
    return schemas.load(_DATE_KEY)


@registries.registry.schemas(_DATE_ISO_KEY)
def _get_date_iso_schema():
    """ returns the schema for date.iso types """
    # NOTE: These all share a schema
    return schemas.load(_DATE_KEY)


@registries.registry.schemas(_DATE_ISO_US_KEY)
def _get_date_iso_us_schema():
    """ returns the schema for date.iso.us types """
    # NOTE: These all share a schema
    return schemas.load(_DATE_KEY)


def _uniform_date_timestamp(
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


def _gauss_date_timestamp(
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


@registries.registry.types(_DATE_KEY)
def _configure_date_supplier(field_spec: dict, loader: Loader):
    """ configures the date value supplier """
    config = utils.load_config(field_spec, loader)
    if 'center_date' in config or 'stddev_days' in config:
        return _create_stats_based_date_supplier(config)
    return _create_uniform_date_supplier(config)


def _create_stats_based_date_supplier(config: dict):
    """ creates stats based date supplier from config """
    center_date = config.get('center_date')
    stddev_days = config.get('stddev_days', registries.get_default('date_stddev_days'))
    date_format = config.get('format', registries.get_default('date_format'))
    timestamp_distribution = _gauss_date_timestamp(center_date, float(stddev_days), date_format)
    return date_supplier(date_format, timestamp_distribution)


def _create_uniform_date_supplier(config):
    """ creates uniform based date supplier from config """
    duration_days = config.get('duration_days', 30)
    offset = int(config.get('offset', 0))
    start = config.get('start')
    end = config.get('end')
    date_format = config.get('format', registries.get_default('date_format'))
    timestamp_distribution = _uniform_date_timestamp(start, end, offset, duration_days, date_format)
    if timestamp_distribution is None:
        raise SpecException(f'Unable to generate timestamp supplier from config: {json.dumps(config)}')
    return date_supplier(date_format, timestamp_distribution)


@registries.registry.types(_DATE_ISO_KEY)
def _configure_supplier_iso(field_spec: dict, loader: Loader):
    """ configures the date.iso value supplier """
    return _configure_supplier_iso_date(field_spec, loader, _ISO_FORMAT_NO_MICRO)


@registries.registry.types(_DATE_ISO_US_KEY)
def _configure_supplier_iso_microseconds(field_spec: dict, loader: Loader):
    """ configures the date.iso.us value supplier """
    return _configure_supplier_iso_date(field_spec, loader, _ISO_FORMAT_WITH_MICRO)


def _configure_supplier_iso_date(field_spec, loader, iso_date_format):
    """ configures an iso based date supplier using the provided date format """
    config = utils.load_config(field_spec, loader)

    # make sure the start and end dates match the ISO format we are using
    start = config.get('start')
    end = config.get('end')
    date_format = config.get('format', )
    if start:
        start_date = datetime.datetime.strptime(start, date_format)
        config['start'] = start_date.strftime(iso_date_format)
    if end:
        end_date = datetime.datetime.strptime(end, date_format)
        config['end'] = end_date.strftime(iso_date_format)
    config['format'] = iso_date_format
    # End fixes to support iso

    if 'center_date' in config or 'stddev_days' in config:
        return _create_stats_based_date_supplier(config)
    return _create_uniform_date_supplier(config)


############
# geo
###########
@registries.registry.schemas(_GEO_LAT_KEY)
def _get_geo_lat_schema():
    return schemas.load(_GEO_LAT_KEY)


@registries.registry.schemas(_GEO_LONG_KEY)
def _get_geo_long_schema():
    return schemas.load(_GEO_LONG_KEY)


@registries.registry.schemas(_GEO_PAIR_KEY)
def _get_geo_pair_schema():
    return schemas.load(_GEO_PAIR_KEY)


@registries.registry.types(_GEO_LAT_KEY)
def _configure_geo_lat(field_spec, loader):
    """ configures value supplier for geo.lat type """
    return _configure_lat_type(field_spec, loader)


@registries.registry.types(_GEO_LONG_KEY)
def _configure_geo_long(field_spec, loader):
    """ configures value supplier for geo.long type """
    return _configure_long_type(field_spec, loader)


@registries.registry.types(_GEO_PAIR_KEY)
def _configure_geo_pair(field_spec, loader):
    """ configures value supplier for geo.pair type """
    config = utils.load_config(field_spec, loader)
    long_supplier = _configure_long_type(field_spec, loader)
    lat_supplier = _configure_lat_type(field_spec, loader)
    join_with = config.get('join_with', registries.get_default('geo_join_with'))
    as_list = utils.is_affirmative('as_list', config, registries.get_default('geo_as_list'))
    lat_first = utils.is_affirmative('lat_first', config, registries.get_default('geo_lat_first'))
    combine_config = {
        'join_with': join_with,
        'as_list': as_list
    }
    if lat_first:
        return suppliers.combine([lat_supplier, long_supplier], combine_config)
    return suppliers.combine([long_supplier, lat_supplier], combine_config)


def _configure_long_type(spec, loader):
    return _configure_geo_type(spec, loader, -180.0, 180.0, '_long')


def _configure_lat_type(spec, loader):
    return _configure_geo_type(spec, loader, -90.0, 90.0, '_lat')


def _configure_geo_type(spec, loader, default_start, default_end, suffix):
    config = utils.load_config(spec, loader)
    precision = config.get('precision', registries.get_default('geo_precision'))
    if not str(precision).isnumeric():
        raise SpecException(f'precision for geo should be valid integer >= 0: {json.dumps(spec)}')
    start, end = _get_start_end(config, default_start, default_end, suffix)
    return suppliers.random_range(start, end, precision)


def _get_start_end(config, default_start, default_end, suffix):
    if 'bbox' in config:
        bbox = config['bbox']
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
    start = config.get('start' + suffix, default_start)
    # end_lat or end_long overrides bbox or defaults
    end = config.get('end' + suffix, default_end)
    return start, end


###########
# nested
##########
@registries.registry.schemas('nested')
def _get_nested_schema():
    return schemas.load('nested')


@registries.registry.types('nested')
def _configure_nested_supplier(spec, loader):
    """ configure the supplier for nested types """
    fields = spec['fields']
    keys = [key for key in fields.keys() if key not in loader.RESERVED]
    config = utils.load_config(spec, loader)
    count_supplier = suppliers.count_supplier_from_data(config.get('count', 1))
    if 'field_groups' in spec:
        key_supplier = key_suppliers.from_spec(spec)
    else:
        key_supplier = key_suppliers.from_spec(fields)

    as_list = utils.is_affirmative('as_list', config)

    field_supplier_map = {}
    # each non reserved key should have a valid spec as a value
    for key in keys:
        nested_spec = fields[key]
        if 'type' in nested_spec and nested_spec.get('type') == 'nested':
            supplier = _configure_nested_supplier(nested_spec, loader)
        else:
            supplier = loader.get_from_spec(nested_spec)
        field_supplier_map[key] = supplier
    return nested_supplier(field_supplier_map, count_supplier, key_supplier, as_list)


###########
# network
###########
@registries.registry.schemas(_IP_KEY)
def _get_ip_schema():
    """ returns the schema for the ip types """
    return schemas.load(_IP_KEY)


@registries.registry.schemas(_IPV4_KEY)
def _get_ipv4_schema():
    """ returns the schema for the ipv4 types """
    # shares schema with ip
    return schemas.load(_IP_KEY)


@registries.registry.schemas(_IP_PRECISE_KEY)
def _get_ip_precise_schema():
    """ returns the schema for the ip.precise types """
    return schemas.load(_IP_PRECISE_KEY)


@registries.registry.schemas(_NET_MAC_KEY)
def _get_mac_addr_schema():
    """ returns the schema for the net.mac types """
    return schemas.load(_NET_MAC_KEY)


@registries.registry.types(_IPV4_KEY)
def _configure_ipv4(field_spec, _):
    """ configures value supplier for ipv4 type """
    return _configure_ip(field_spec, _)


@registries.registry.types(_IP_KEY)
def _configure_ip(field_spec, loader):
    """ configures value supplier for ip type """
    config = utils.load_config(field_spec, loader)
    if 'base' in config and 'cidr' in config:
        raise SpecException('Must supply only one of base or cidr param: ' + json.dumps(field_spec))

    parts = _get_base_parts(config)
    # this is the same thing as a constant
    if len(parts) == 4:
        return suppliers.values('.'.join(parts))
    sample = config.get('sample', 'yes')
    octet_supplier_map = {
        'first': _create_octet_supplier(parts, 0, sample),
        'second': _create_octet_supplier(parts, 1, sample),
        'third': _create_octet_supplier(parts, 2, sample),
        'fourth': _create_octet_supplier(parts, 3, sample),
    }
    return ipv4(octet_supplier_map)


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
        if '/' in cidr:
            mask = cidr[cidr.index('/') + 1:]
            if not mask.isdigit():
                raise SpecException('Invalid Mask in cidr for config: ' + json.dumps(config))
            if int(mask) not in [8, 16, 24]:
                raise SpecException('Invalid Subnet Mask in cidr for config: ' + json.dumps(config)
                                    + ' only one of /8 /16 or /24 supported')
            ip_parts = cidr[0:cidr.index('/')].split('.')
            if len(ip_parts) < 4 or not all(part.isdigit() for part in ip_parts):
                raise SpecException('Invalid IP in cidr for config: ' + json.dumps(config))
            if mask == '8':
                parts = ip_parts[0:1]
            if mask == '16':
                parts = ip_parts[0:2]
            if mask == '24':
                parts = ip_parts[0:3]
        else:
            raise SpecException('Invalid Subnet Mask in cidr for config: ' + json.dumps(config)
                                + ' only one of /8 /16 or /24 supported')
    return parts


def _create_octet_supplier(parts, index, sample):
    """ creates a value supplier for the index'th octet """
    # this index is for a part that is static, create a single value supplier for that part
    if len(parts) >= index + 1 and parts[index].strip() != '':
        octet = parts[index].strip()
        if not octet.isdigit():
            raise SpecException(f'Octet: {octet} invalid for base, Invalid Input: ' + '.'.join(parts))
        if not 0 <= int(octet) <= 255:
            raise SpecException(
                f'Each octet: {octet} must be in range of 0 to 255, Invalid Input: ' + '.'.join(parts))
        return suppliers.values(octet)
    # need octet range at this point
    octet_range = list(range(0, 255))
    spec = {'config': {'sample': sample}, 'data': octet_range}
    return suppliers.values(spec)


@registries.registry.types(_IP_PRECISE_KEY)
def _configure_precise_ip(field_spec, _):
    """ configures value supplier for ip.precise type """
    config = field_spec.get('config')
    if config is None:
        raise SpecException('No config for: ' + json.dumps(field_spec) + ', param cidr required')
    cidr = config.get('cidr')
    sample = config.get('sample', 'no').lower() in ['yes', 'true', 'on']
    if cidr is None:
        raise SpecException('Invalid config for: ' + json.dumps(field_spec) + ', param cidr required')
    return ip_precise(cidr, sample)


@registries.registry.types(_NET_MAC_KEY)
def _configure_mac_address_supplier(field_spec, loader):
    """ configures value supplier for net.mac type """
    config = utils.load_config(field_spec, loader)
    if utils.is_affirmative('dashes', config):
        delim = '-'
    else:
        delim = registries.get_default('mac_addr_separator')

    return mac_address(delim)


###################
# range_suppliers
###################
@registries.registry.schemas(_RANGE_KEY)
def _get_range_schema():
    """ schema for range type """
    return schemas.load(_RANGE_KEY)


@registries.registry.schemas(_RAND_RANGE_KEY)
def _get_rand_range_schema():
    """ schema for rand range type """
    # This shares a schema with range
    return schemas.load(_RANGE_KEY)


@registries.registry.schemas(_RAND_INT_RANGE_KEY)
def _get_rand_int_range_schema():
    """ schema for rand int range type """
    # This shares a schema with range
    return schemas.load(_RANGE_KEY)


@registries.registry.types(_RANGE_KEY)
def _configure_range_supplier(field_spec, _):
    """ configures the range value supplier """
    if 'data' not in field_spec:
        raise SpecException('No data element defined for: %s' % json.dumps(field_spec))

    data = field_spec.get('data')
    if not isinstance(data, list) or len(data) < 2:
        raise SpecException(
            'data element for ranges type must be list with at least two elements: %s' % json.dumps(field_spec))
    # we have the nested case
    if isinstance(data[0], list):
        suppliers_list = [_configure_supplier_for_data(field_spec, subdata) for subdata in data]
        return suppliers.from_list_of_suppliers(suppliers_list, True)
    return _configure_supplier_for_data(field_spec, data)


def _configure_supplier_for_data(field_spec, data):
    """ configures the supplier based on the range data supplied """
    start = data[0]
    # default for built in range function is exclusive end, we want to default to inclusive as this is the
    # more intuitive behavior
    end = data[1] + 1
    if not end > start:
        raise SpecException('end element must be larger than start: %s' % json.dumps(field_spec))
    if len(data) == 2:
        step = 1
    else:
        step = data[2]
    if _any_is_float(data):
        config = field_spec.get('config', {})
        precision = config.get('precision', None)
        if precision and not str(precision).isnumeric():
            raise SpecException(f'precision must be valid integer {json.dumps(field_spec)}')
        range_values = list(_float_range(float(start), float(end), float(step), precision))
    else:
        range_values = list(range(start, end, step))
    return suppliers.values(range_values)


@registries.registry.types(_RAND_INT_RANGE_KEY)
def _configure_rand_int_range_supplier(field_spec, loader):
    """ configures the random int range value supplier """
    config = utils.load_config(field_spec, loader)
    config['cast'] = 'int'
    field_spec['config'] = config
    return _configure_rand_range_supplier(field_spec, loader)


@registries.registry.types(_RAND_RANGE_KEY)
def _configure_rand_range_supplier(field_spec, loader):
    """ configures the random range value supplier """
    if 'data' not in field_spec:
        raise SpecException('No data element defined for: %s' % json.dumps(field_spec))
    data = field_spec.get('data')
    config = utils.load_config(field_spec, loader)
    if not isinstance(data, list) or len(data) == 0:
        raise SpecException(
            'rand_range specs require data as array with at least one element: %s' % json.dumps(field_spec))
    start = 0
    end = 0
    if len(data) == 1:
        end = data[0]
    if len(data) >= 2:
        start = data[0]
        end = data[1]
    precision = None
    if len(data) > 2:
        precision = data[2]
    # config overrides third data element if specified
    precision = config.get('precision', precision)
    return suppliers.random_range(start, end, precision)


def _any_is_float(data):
    """ are any of the items floats """
    for item in data:
        if isinstance(item, float):
            return True
    return False


def _float_range(start: float,
                 stop: float,
                 step: float,
                 precision=None):
    """
    Fancy foot work to support floating point ranges due to rounding errors with the way floating point numbers are
    stored
    """
    # attempt to defeat some rounding errors prevalent in python
    current = decimal.Decimal(str(start))
    if precision:
        quantize = decimal.Decimal(str(1 / math.pow(10, int(precision))))
        current = current.quantize(quantize)

    dstop = decimal.Decimal(str(stop))
    dstep = decimal.Decimal(str(step))
    while current < dstop:
        # inefficient?
        yield float(str(current))
        current = current + dstep
        if precision:
            current = current.quantize(quantize)


###################
# refs
###################
@registries.registry.schemas('ref')
def _get_ref_schema():
    return schemas.load('ref')


@registries.registry.types('ref')
def _configure_ref_supplier(field_spec: dict, loader: Loader):
    """ configures supplier for ref type """
    key = None
    if 'data' in field_spec:
        key = field_spec.get('data')
    if 'ref' in field_spec:
        key = field_spec.get('ref')
    if key is None:
        raise SpecException('No key found for spec: ' + json.dumps(field_spec))
    return loader.get(key)


@registries.registry.schemas(_WEIGHTED_REF_KEY)
def _weighted_ref_schema():
    return schemas.load(_WEIGHTED_REF_KEY)


@registries.registry.types(_WEIGHTED_REF_KEY)
def _configure_weighted_ref_supplier(parent_field_spec, loader):
    """ configures supplier for weighted ref specs """
    config = utils.load_config(parent_field_spec, loader)
    data = parent_field_spec['data']
    key_supplier = suppliers.values(data)
    values_map = {}
    for key in data.keys():
        supplier = loader.get(key)
        values_map[key] = supplier
    supplier = weighted_ref_supplier(key_supplier, values_map)
    if 'count' in config:
        return suppliers.array_supplier(supplier, config)
    return supplier


####################
# select_list_subset
####################
@registries.registry.schemas(_SELECT_LIST_SUBSET_KEY)
def _select_list_subset_schema():
    return schemas.load(_SELECT_LIST_SUBSET_KEY)


@registries.registry.types(_SELECT_LIST_SUBSET_KEY)
def _configure_select_list_subset_supplier(field_spec, loader):
    """ configures supplier for select_list_subset type """
    config = utils.load_config(field_spec, loader)
    if config is None or ('mean' not in config and 'count' not in config):
        raise SpecException('Config with mean or count defined must be provided: %s' % json.dumps(field_spec))
    if 'ref' in field_spec and 'data' in field_spec:
        raise SpecException('Only one of "data" or "ref" can be provided for: %s' % json.dumps(field_spec))

    if 'ref' in field_spec:
        ref_name = field_spec.get('ref')
        field_spec = loader.get_ref_spec(ref_name)
        if field_spec is None:
            raise SpecException('No ref with name %s found: %s' % (ref_name, json.dumps(field_spec)))

        if 'data' in field_spec:
            data = field_spec.get('data')
        else:
            data = field_spec
    elif 'data' in field_spec:
        data = field_spec.get('data')
    if utils.any_key_exists(config, ['mean', 'stddev']):
        return suppliers.list_stat_sampler(data, config)
    return suppliers.list_count_sampler(data, config)


###################
# unicode_range
###################


@registries.registry.schemas(_UNICODE_RANGE_KEY)
def _get_unicode_range_schema():
    """ get the unicode range schema """
    return schemas.load(_UNICODE_RANGE_KEY)


@registries.registry.types(_UNICODE_RANGE_KEY)
def _configure_unicode_range_supplier(spec, _):
    """ configure the supplier for unicode_range types """
    if 'data' not in spec:
        raise SpecException('data is Required Element for unicode_range specs: ' + json.dumps(spec))
    data = spec['data']
    if not isinstance(data, list):
        raise SpecException(
            f'data should be a list or list of lists with two elements for {_UNICODE_RANGE_KEY} specs: ' + json.dumps(
                spec))
    config = spec.get('config', {})
    if isinstance(data[0], list):
        suppliers_list = [_single_range(sublist, config) for sublist in data]
        return suppliers.from_list_of_suppliers(suppliers_list, True)
    return _single_range(data, config)


def _single_range(data, config):
    """ creates a unicode supplier for a single unicode range """
    # supplies range of data as floats
    range_data = list(range(_decode_num(data[0]), _decode_num(data[1]) + 1))
    # casts the floats to ints
    if utils.any_key_exists(config, ['mean', 'stddev']):
        if 'as_list' not in config:
            config['as_list'] = 'true'
        wrapped = suppliers.list_stat_sampler(range_data, config)
    else:
        wrapped = suppliers.list_count_sampler(range_data, config)
    return unicode_range_supplier(wrapped)


def _decode_num(num):
    """ decodes the num if hex encoded """
    if isinstance(num, str):
        return int(num, 16)
    return int(num)


#################
# uuid_handler
#################
@registries.registry.schemas(_UUID_KEY)
def _get_uuid_schema():
    """ get the schema for uuid type """
    return schemas.load(_UUID_KEY)


@registries.registry.types(_UUID_KEY)
def _configure_uuid_supplier(field_spec, loader):
    """ configure the supplier for uuid types """
    config = utils.load_config(field_spec, loader)
    variant = int(config.get('variant', 4))

    if variant not in [1, 3, 4, 5]:
        raise SpecException('Invalid variant for: ' + field_spec)
    return uuid_supplier(variant)
