"""
Module for storing default settings across package
"""
import logging
from . import registries

_LARGE_CSV_SIZE_MB = 250


@registries.Registry.defaults('sample_mode')
def _default_list_sample_mode():
    """ By default we do not sample from lists backed types """
    return False


@registries.Registry.defaults('unicode_join_with')
@registries.Registry.defaults('char_class_join_with')
@registries.Registry.defaults('combine_join_with')
def _default_char_class_join_with():
    """ default join for char_class and combine types """
    return ''


@registries.Registry.defaults('combine_as_list')
@registries.Registry.defaults('geo_as_list')
def _default_as_list_false():
    """ default as list for combine and geo types """
    return False


@registries.Registry.defaults('geo_lat_first')
def _default_geo_lat_first():
    """ default lat first for geo types """
    return False


@registries.Registry.defaults('geo_join_with')
def _default_geo_join_with():
    """ default join for geo types """
    return ','


@registries.Registry.defaults('date_stddev_days')
def _default_date_stddev_days():
    """ default date stddev days """
    return 15


@registries.Registry.defaults('date_format')
def _default_date_format():
    """ default date format """
    return "%d-%m-%Y"


@registries.Registry.defaults('date_duration_days')
def _default_date_duration_days():
    """ default date duration days """
    return 30


@registries.Registry.defaults('geo_precision')
def _default_geo_type_precision():
    """ default digits after decimal for geo types """
    return 4


@registries.Registry.defaults('json_indent')
def _default_json_indent():
    """ default spaces to indent when using json-pretty formatter """
    return 4


@registries.Registry.defaults('large_csv_size_mb')
def _default_large_csv_size():
    """ default size for what constitutes a large csv file """
    return _LARGE_CSV_SIZE_MB


@registries.Registry.defaults('data_dir')
def _default_data_dir():
    """ default location for data directory """
    return './data'


@registries.Registry.defaults('csv_file')
def _default_csv_file():
    """ default name for csv files """
    return 'data.csv'


@registries.Registry.defaults('mac_addr_separator')
def _default_mac_address_separator():
    """ default mac address separator """
    return ':'


@registries.Registry.defaults('outfile_prefix')
def _default_outfile_prefix():
    """ default output file prefix """
    return 'generated'


@registries.Registry.defaults('outfile_extension')
def _default_outfile_extension():
    """ default output file extension """
    return ''


@registries.Registry.defaults('log_level')
def _default_log_level():
    """ default logging level """
    return logging.INFO


@registries.Registry.defaults('strict_mode')
def _default_strict_mode():
    """ default strict schema checking enabled """
    return False


@registries.Registry.defaults('exclude_internal')
def _default_exclude_internal():
    """ default if internal fields should be excluded from output """
    return False


@registries.Registry.defaults('sample_lists')
def _default_sample_lists():
    """ default if lists should be sampled """
    return False


@registries.Registry.defaults('uuid_variant')
def _default_uuid_variant():
    """ default uuid variant """
    return 4


@registries.Registry.defaults('format_json_ascii')
def _default_format_json_ascii():
    """ if the JSON formatted data should be ascii """
    return False
