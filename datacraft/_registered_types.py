"""
Internal module where the built in types are registered and configured
"""
import csv
import datetime
import json
import logging
import os
import string

from . import distributions, suppliers, registries, schemas, utils
from .exceptions import SpecException
from .loader import Loader
from .supplier import key_suppliers
from .supplier.common import weighted_values_explicit
# for nested
from .supplier.nested import nested_supplier
# for refs
from .supplier.refs import weighted_ref_supplier
# for unicode ranges
from .supplier.unicode import unicode_range_supplier
# for calculate
from .suppliers import calculate

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
_CSV_TYPE = 'csv'
_WEIGHTED_CSV = 'weighted_csv'
_IP_KEY = 'ip'
_IPV4_KEY = 'ipv4'
_IP_PRECISE_KEY = 'ip.precise'
_NET_MAC_KEY = 'net.mac'
_RANGE_KEY = 'range'
_RAND_RANGE_KEY = 'rand_range'
_RAND_INT_RANGE_KEY = 'rand_int_range'
_REF_KEY = 'ref'
_WEIGHTED_REF_KEY = 'weighted_ref'
_SELECT_LIST_SUBSET_KEY = 'select_list_subset'
_UNICODE_RANGE_KEY = 'unicode_range'
_UUID_KEY = 'uuid'
_DISTRIBUTION_KEY = 'distribution'
_TEMPLATED_KEY = 'templated'

_log = logging.getLogger('datacraft.types')


##############
# values
##############
@registries.Registry.schemas(_VALUES_KEY)
def _get_values_schema():
    """ returns the values schema """
    return schemas.load(_VALUES_KEY)


@registries.Registry.types(_VALUES_KEY)
def _handle_values_type(spec, loader):
    """ handles values types """
    config = utils.load_config(spec, loader)
    return suppliers.values(spec, **config)


##############
# calculate
##############
@registries.Registry.schemas(_CALCULATE_KEY)
def _calculate_schema():
    """ get the schema for the calculate type """
    return schemas.load(_CALCULATE_KEY)


@registries.Registry.types(_CALCULATE_KEY)
def _configure_calculate_supplier(field_spec: dict, loader: Loader):
    """ configures supplier for calculate type """

    formula = field_spec.get('formula')
    if formula is None:
        raise SpecException('Must define formula for calculate type. %s' % json.dumps(field_spec))

    suppliers_map = _build_suppliers_map(field_spec, loader)

    return calculate(suppliers_map=suppliers_map, formula=formula)


@registries.Registry.schemas(_TEMPLATED_KEY)
def _templated_schema():
    return schemas.load(_TEMPLATED_KEY)


@registries.Registry.types(_TEMPLATED_KEY)
def _configure_templated_type(field_spec, loader):
    if 'data' not in field_spec:
        raise SpecException(f'data is required field for templated specs: {json.dumps(field_spec)}')
    suppliers_map = _build_suppliers_map(field_spec, loader)

    return suppliers.templated(suppliers_map, field_spec.get('data', None))


def _build_suppliers_map(field_spec, loader):
    if 'refs' not in field_spec and 'fields' not in field_spec:
        raise SpecException('Must define one of fields or refs. %s' % json.dumps(field_spec))
    if 'refs' in field_spec and 'fields' in field_spec:
        raise SpecException('Must define only one of fields or refs. %s' % json.dumps(field_spec))
    mappings = _get_mappings(field_spec, 'refs')
    mappings.update(_get_mappings(field_spec, 'fields'))
    if len(mappings) < 1:
        raise SpecException('fields or refs empty: %s' % json.dumps(field_spec))
    suppliers_map = {}
    for field_or_ref, alias in mappings.items():
        supplier = loader.get(field_or_ref)
        suppliers_map[alias] = supplier
    return suppliers_map


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


@registries.Registry.schemas(_CHAR_CLASS_KEY)
def _get_char_class_schema():
    """ get the schema for the char_class type """
    return schemas.load(_CHAR_CLASS_KEY)


for class_key in _CLASS_MAPPING:
    @registries.Registry.schemas("cc-" + class_key)
    def _get_char_class_alias_schema():
        """ get the schema for the char_class type """
        return schemas.load(_CHAR_CLASS_KEY)


@registries.Registry.types(_CHAR_CLASS_KEY)
def _configure_char_class_supplier(spec, loader):
    """ configure the supplier for char_class types """
    if 'data' not in spec:
        raise SpecException(f'Data is required field for char_class type: {json.dumps(spec)}')
    config = utils.load_config(spec, loader)
    data = spec['data']
    if isinstance(data, str) and data in _CLASS_MAPPING:
        data = _CLASS_MAPPING[data]
    if isinstance(data, list):
        new_data = [_CLASS_MAPPING[datum] if datum in _CLASS_MAPPING else datum for datum in data]
        data = ''.join(new_data)

    if 'join_with' not in config:
        config['join_with'] = registries.get_default('char_class_join_with')

    return suppliers.character_class(data, **config)


for class_key in _CLASS_MAPPING:
    @registries.Registry.types("cc-" + class_key)
    def _configure_char_class_alias_supplier(spec, loader):
        """ configure the supplier for char_class alias types """
        spec['data'] = class_key
        return _configure_char_class_supplier(spec, loader)


############
# combine
############
@registries.Registry.schemas(_COMBINE_KEY)
def _get_combine_schema():
    """ get the schema for the combine type """
    return schemas.load(_COMBINE_KEY)


@registries.Registry.schemas(_COMBINE_LIST_KEY)
def _get_combine_list_schema():
    """ get the schema for the combine_list type """
    return schemas.load(_COMBINE_LIST_KEY)


@registries.Registry.types(_COMBINE_KEY)
def _configure_combine_supplier(field_spec, loader):
    """ configures supplier for combine type """
    if 'refs' not in field_spec and 'fields' not in field_spec:
        raise SpecException('Must define one of fields or refs. %s' % json.dumps(field_spec))

    if 'refs' in field_spec:
        supplier = _load_combine_from_refs(field_spec, loader)
    else:
        supplier = _load_combine_from_fields(field_spec, loader)
    return supplier


@registries.Registry.types(_COMBINE_LIST_KEY)
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
    return suppliers.combine(to_combine, joiner, as_list)


############
# config_ref
############
@registries.Registry.types('config_ref')
def _config_ref_handler(_, __):
    """" Does nothing, just place holder """


########
# csv
#######


@registries.Registry.types(_CSV_TYPE)
def _configure_csv(field_spec, loader):
    """ Configures the csv value supplier for this field """
    config = utils.load_config(field_spec, loader)
    datafile = config.get('datafile', registries.get_default('csv_file'))
    csv_path = f'{loader.datadir}/{datafile}'
    if not os.path.exists(csv_path):
        raise SpecException(f'Unable to locate data file: {datafile} in data dir: {loader.datadir} for spec: '
                            + json.dumps(field_spec))
    return suppliers.csv(csv_path, **config)


@registries.Registry.schemas(_CSV_TYPE)
def _get_csv_schema():
    """ get the schema for the csv type """
    return schemas.load(_CSV_TYPE)


@registries.Registry.types(_WEIGHTED_CSV)
def _configure_weighted_csv(field_spec, loader):
    """ Configures the weighted_csv value supplier for this field """

    config = utils.load_config(field_spec, loader)

    field_name = config.get('column', 1)
    weight_column = config.get('weight_column', 2)
    count_supplier = suppliers.count_supplier(**config)

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


@registries.Registry.schemas(_WEIGHTED_CSV)
def _get_weighted_csv_schema():
    """ get the schema for the weighted_csv type """
    return schemas.load(_WEIGHTED_CSV)


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


#######
# date
#######
_ISO_FORMAT_NO_MICRO = '%Y-%m-%dT%H:%M:%S'
_ISO_FORMAT_WITH_MICRO = '%Y-%m-%dT%H:%M:%S.%f'


@registries.Registry.schemas(_DATE_KEY)
def _get_date_schema():
    """ returns the schema for date types """
    return schemas.load(_DATE_KEY)


@registries.Registry.schemas(_DATE_ISO_KEY)
def _get_date_iso_schema():
    """ returns the schema for date.iso types """
    # NOTE: These all share a schema
    return schemas.load(_DATE_KEY)


@registries.Registry.schemas(_DATE_ISO_US_KEY)
def _get_date_iso_us_schema():
    """ returns the schema for date.iso.us types """
    # NOTE: These all share a schema
    return schemas.load(_DATE_KEY)


@registries.Registry.types(_DATE_KEY)
def _configure_date_supplier(field_spec: dict, loader: Loader):
    """ configures the date value supplier """
    config = utils.load_config(field_spec, loader)
    config['hour_supplier'] = _hour_supplier(config, loader)
    return suppliers.date(**config)


def _hour_supplier(config: dict, loader: Loader):
    """ get hour supplier from config if present """
    if 'hours' not in config:
        return None
    return loader.get_from_spec(config['hours'])


@registries.Registry.types(_DATE_ISO_KEY)
def _configure_supplier_iso(field_spec: dict, loader: Loader):
    """ configures the date.iso value supplier """
    return _configure_supplier_iso_date(field_spec, loader, _ISO_FORMAT_NO_MICRO)


@registries.Registry.types(_DATE_ISO_US_KEY)
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
    config['hour_supplier'] = _hour_supplier(config, loader)
    return suppliers.date(**config)


############
# geo
###########
@registries.Registry.schemas(_GEO_LAT_KEY)
def _get_geo_lat_schema():
    """ schema for geo.lat type """
    return schemas.load(_GEO_LAT_KEY)


@registries.Registry.schemas(_GEO_LONG_KEY)
def _get_geo_long_schema():
    """ schema for geo.long type """
    return schemas.load(_GEO_LONG_KEY)


@registries.Registry.schemas(_GEO_PAIR_KEY)
def _get_geo_pair_schema():
    """ schema for geo.pair type """
    return schemas.load(_GEO_PAIR_KEY)


@registries.Registry.types(_GEO_LAT_KEY)
def _configure_geo_lat(field_spec, loader):
    """ configures value supplier for geo.lat type """
    config = utils.load_config(field_spec, loader)
    return suppliers.geo_lat(**config)


@registries.Registry.types(_GEO_LONG_KEY)
def _configure_geo_long(field_spec, loader):
    """ configures value supplier for geo.long type """
    config = utils.load_config(field_spec, loader)
    return suppliers.geo_long(**config)


@registries.Registry.types(_GEO_PAIR_KEY)
def _configure_geo_pair(field_spec, loader):
    """ configures value supplier for geo.pair type """
    config = utils.load_config(field_spec, loader)
    return suppliers.geo_pair(**config)


###########
# nested
##########
@registries.Registry.schemas('nested')
def _get_nested_schema():
    """ schema for nested type """
    return schemas.load('nested')


@registries.Registry.types('nested')
def _configure_nested_supplier(spec, loader):
    """ configure the supplier for nested types """
    fields = spec['fields']
    keys = [key for key in fields.keys()]
    config = utils.load_config(spec, loader)
    count_supplier = suppliers.count_supplier(**config)
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
@registries.Registry.schemas(_IP_KEY)
def _get_ip_schema():
    """ returns the schema for the ip types """
    return schemas.load(_IP_KEY)


@registries.Registry.schemas(_IPV4_KEY)
def _get_ipv4_schema():
    """ returns the schema for the ipv4 types """
    # shares schema with ip
    return schemas.load(_IP_KEY)


@registries.Registry.schemas(_IP_PRECISE_KEY)
def _get_ip_precise_schema():
    """ returns the schema for the ip.precise types """
    return schemas.load(_IP_PRECISE_KEY)


@registries.Registry.schemas(_NET_MAC_KEY)
def _get_mac_addr_schema():
    """ returns the schema for the net.mac types """
    return schemas.load(_NET_MAC_KEY)


@registries.Registry.types(_IPV4_KEY)
@registries.Registry.types(_IP_KEY)
def _configure_ip(field_spec, loader):
    """ configures value supplier for ip type """
    config = utils.load_config(field_spec, loader)
    try:
        return suppliers.ip_supplier(**config)
    except ValueError as err:
        raise SpecException(str(err)) from err


@registries.Registry.types(_IP_PRECISE_KEY)
def _configure_precise_ip(field_spec, _):
    """ configures value supplier for ip.precise type """
    config = field_spec.get('config')
    if config is None:
        raise SpecException('No config for: ' + json.dumps(field_spec) + ', param cidr required')
    cidr = config.get('cidr')
    sample = utils.is_affirmative('sample', config, 'no')
    if cidr is None:
        raise SpecException('Invalid config for: ' + json.dumps(field_spec) + ', param cidr required')
    return suppliers.ip_precise(cidr, sample)


@registries.Registry.types(_NET_MAC_KEY)
def _configure_mac_address_supplier(field_spec, loader):
    """ configures value supplier for net.mac type """
    config = utils.load_config(field_spec, loader)
    if utils.is_affirmative('dashes', config):
        delim = '-'
    else:
        delim = registries.get_default('mac_addr_separator')

    return suppliers.mac_address(delim)


###################
# range_suppliers
###################
@registries.Registry.schemas(_RANGE_KEY)
def _get_range_schema():
    """ schema for range type """
    return schemas.load(_RANGE_KEY)


@registries.Registry.schemas(_RAND_RANGE_KEY)
def _get_rand_range_schema():
    """ schema for rand range type """
    # This shares a schema with range
    return schemas.load(_RANGE_KEY)


@registries.Registry.schemas(_RAND_INT_RANGE_KEY)
def _get_rand_int_range_schema():
    """ schema for rand int range type """
    # This shares a schema with range
    return schemas.load(_RANGE_KEY)


@registries.Registry.types(_RANGE_KEY)
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
        suppliers_list = [_configure_range_supplier_for_data(field_spec, subdata) for subdata in data]
        return suppliers.from_list_of_suppliers(suppliers_list, True)
    return _configure_range_supplier_for_data(field_spec, data)


def _configure_range_supplier_for_data(field_spec, data):
    """ configures the supplier based on the range data supplied """
    config = field_spec.get('config', {})
    precision = config.get('precision', None)
    if precision and not str(precision).isnumeric():
        raise SpecException(f'precision must be valid integer {json.dumps(field_spec)}')

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
    try:
        return suppliers.range_supplier(start, end, step, precision=precision)
    except ValueError as err:
        raise SpecException(str(err)) from err


@registries.Registry.types(_RAND_INT_RANGE_KEY)
def _configure_rand_int_range_supplier(field_spec, loader):
    """ configures the random int range value supplier """
    config = utils.load_config(field_spec, loader)
    config['cast'] = 'int'
    field_spec['config'] = config
    return _configure_rand_range_supplier(field_spec, loader)


@registries.Registry.types(_RAND_RANGE_KEY)
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


###################
# refs
###################
@registries.Registry.schemas(_REF_KEY)
def _get_ref_schema():
    """ schema for ref type """
    return schemas.load(_REF_KEY)


@registries.Registry.types(_REF_KEY)
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


@registries.Registry.schemas(_WEIGHTED_REF_KEY)
def _weighted_ref_schema():
    """ schema for weighted_ref type """
    return schemas.load(_WEIGHTED_REF_KEY)


@registries.Registry.types(_WEIGHTED_REF_KEY)
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
        return suppliers.array_supplier(supplier, **config)
    return supplier


####################
# select_list_subset
####################
@registries.Registry.schemas(_SELECT_LIST_SUBSET_KEY)
def _select_list_subset_schema():
    """ schema for select_list_subset type """
    return schemas.load(_SELECT_LIST_SUBSET_KEY)


@registries.Registry.types(_SELECT_LIST_SUBSET_KEY)
def _configure_select_list_subset_supplier(field_spec, loader):
    """ configures supplier for select_list_subset type """
    config = utils.load_config(field_spec, loader)
    if config is None or ('mean' not in config and 'count' not in config):
        raise SpecException('Config with mean or count defined must be provided: %s' % json.dumps(field_spec))
    if 'ref' in field_spec and 'data' in field_spec:
        raise SpecException('Only one of "data" or "ref" can be provided for: %s' % json.dumps(field_spec))

    if 'ref' in field_spec:
        ref_name = field_spec.get('ref')
        field_spec = loader.get_ref(ref_name)
        if field_spec is None:
            raise SpecException('No ref with name %s found: %s' % (ref_name, json.dumps(field_spec)))

        if 'data' in field_spec:
            data = field_spec.get('data')
        else:
            data = field_spec
    elif 'data' in field_spec:
        data = field_spec.get('data')
    return suppliers.select_list_subset(data, **config)


###################
# unicode_range
###################
@registries.Registry.schemas(_UNICODE_RANGE_KEY)
def _get_unicode_range_schema():
    """ get the unicode range schema """
    return schemas.load(_UNICODE_RANGE_KEY)


@registries.Registry.types(_UNICODE_RANGE_KEY)
def _configure_unicode_range_supplier(spec, loader):
    """ configure the supplier for unicode_range types """
    if 'data' not in spec:
        raise SpecException('data is Required Element for unicode_range specs: ' + json.dumps(spec))
    data = spec['data']
    if not isinstance(data, list):
        raise SpecException(
            f'data should be a list or list of lists with two elements for {_UNICODE_RANGE_KEY} specs: ' + json.dumps(
                spec))
    config = utils.load_config(spec, loader)
    return suppliers.unicode_range(data, **config)


#################
# uuid_handler
#################
@registries.Registry.schemas(_UUID_KEY)
def _get_uuid_schema():
    """ get the schema for uuid type """
    return schemas.load(_UUID_KEY)


@registries.Registry.types(_UUID_KEY)
def _configure_uuid_supplier(field_spec, loader):
    """ configure the supplier for uuid types """
    config = utils.load_config(field_spec, loader)
    variant = int(config.get('variant', registries.get_default('uuid_variant')))

    if variant not in [1, 3, 4, 5]:
        raise SpecException('Invalid variant for: ' + json.dumps(field_spec))
    return suppliers.uuid(variant)


###################
# distribution
###################
@registries.Registry.schemas(_DISTRIBUTION_KEY)
def _get_distribution_schema():
    """ get the schema for distribution type """
    return schemas.load(_DISTRIBUTION_KEY)


@registries.Registry.types(_DISTRIBUTION_KEY)
def _configure_distribution_supplier(field_spec, loader):
    """ configure the supplier for distribution types """
    if 'data' not in field_spec:
        raise SpecException(
            'required data element not defined for ' + _DISTRIBUTION_KEY + ' type : ' + json.dumps(field_spec))
    distribution = distributions.from_string(field_spec['data'])
    return suppliers.distribution_supplier(distribution)

