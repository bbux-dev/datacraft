"""
Module for storing default settings across package
"""
from . import registry

LARGE_CSV_SIZE_MB = 250


@registry.defaults('sample_mode')
def _default_list_sample_mode():
    """ By default we do not sample from lists backed types """
    return False


@registry.defaults('char_class_join_with')
@registry.defaults('combine_join_with')
def _default_char_class_join_with():
    """ default join for char_class and combine types """
    return ''


@registry.defaults('combine_as_list')
@registry.defaults('geo_as_list')
def _default_as_list_false():
    """ default as list for combine and geo types """
    return False


@registry.defaults('geo_lat_first')
def _default_geo_lat_first():
    """ default lat first for geo types """
    return False


@registry.defaults('geo_join_with')
def _default_geo_join_with():
    """ default join for geo types """
    return ','


@registry.defaults('date_stddev_days')
def _default_date_stddev_days():
    """ default date stddev days """
    return 15


@registry.defaults('date_format')
def _default_date_format():
    """ default date format """
    return "%d-%m-%Y"


@registry.defaults('geo_precision')
def _default_geo_type_precision():
    """ default digits after decimal for geo types """
    return 4


@registry.defaults('json_indent')
def _default_json_indent():
    """ default spaces to indent when using json-pretty formatter """
    return 4


@registry.defaults('large_csv_size_mb')
def _default_large_csv_size():
    """ default size for what constitutes a large csv file """
    return LARGE_CSV_SIZE_MB


@registry.defaults('data_dir')
def _default_data_dir():
    """ default location for data directory """
    return './data'


@registry.defaults('csv_file')
def _default_csv_file():
    """ default name for csv files """
    return 'data.csv'


@registry.defaults('mac_addr_separator')
def _default_mac_address_separator():
    return ':'


@registry.defaults('outfileprefix')
def _default_outfileprefix():
    return 'generated-'
