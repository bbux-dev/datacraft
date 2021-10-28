"""
Module for handling geo types
"""
import json

import datagen

GEO_LAT_KEY = 'geo.lat'
GEO_LONG_KEY = 'geo.long'
GEO_PAIR_KEY = 'geo.pair'


class GeoSupplier(datagen.ValueSupplierInterface):
    """
    Default implementation for generating geo related values
    """

    def __init__(self, wrapped):
        self.wrapped = wrapped

    def next(self, iteration):
        value = self.wrapped.next(iteration)
        return value


@datagen.registry.schemas(GEO_LAT_KEY)
def _get_geo_lat_schema():
    return datagen.schemas.load(GEO_LAT_KEY)


@datagen.registry.schemas(GEO_LONG_KEY)
def _get_geo_long_schema():
    return datagen.schemas.load(GEO_LONG_KEY)


@datagen.registry.schemas(GEO_PAIR_KEY)
def _get_geo_pair_schema():
    return datagen.schemas.load(GEO_PAIR_KEY)


@datagen.registry.types(GEO_LAT_KEY)
def _configure_geo_lat(field_spec, loader):
    """ configures value supplier for geo.lat type """
    return _configure_lat_type(field_spec, loader)


@datagen.registry.types(GEO_LONG_KEY)
def _configure_geo_long(field_spec, loader):
    """ configures value supplier for geo.long type """
    return _configure_long_type(field_spec, loader)


@datagen.registry.types(GEO_PAIR_KEY)
def _configure_geo_pair(field_spec, loader):
    """ configures value supplier for geo.pair type """
    config = datagen.utils.load_config(field_spec, loader)
    long_supplier = _configure_long_type(field_spec, loader)
    lat_supplier = _configure_lat_type(field_spec, loader)
    join_with = config.get('join_with', datagen.types.get_default('geo_join_with'))
    as_list = datagen.utils.is_affirmative('as_list', config, datagen.types.get_default('geo_as_list'))
    lat_first = datagen.utils.is_affirmative('lat_first', config, datagen.types.get_default('geo_lat_first'))
    combine_config = {
        'join_with': join_with,
        'as_list': as_list
    }
    if lat_first:
        return datagen.suppliers.combine([lat_supplier, long_supplier], combine_config)
    return datagen.suppliers.combine([long_supplier, lat_supplier], combine_config)


def _configure_long_type(spec, loader):
    return _configure_geo_type(spec, loader, -180.0, 180.0, '_long')


def _configure_lat_type(spec, loader):
    return _configure_geo_type(spec, loader, -90.0, 90.0, '_lat')


def _configure_geo_type(spec, loader, default_start, default_end, suffix):
    config = datagen.utils.load_config(spec, loader)
    precision = config.get('precision', datagen.types.get_default('geo_precision'))
    if not str(precision).isnumeric():
        raise datagen.SpecException(f'precision for geo should be valid integer: {json.dumps(spec)}')
    start, end = _get_start_end(config, default_start, default_end, suffix)
    return GeoSupplier(datagen.suppliers.random_range(start, end, precision))


def _get_start_end(config, default_start, default_end, suffix):
    if 'bbox' in config:
        bbox = config['bbox']
        if not isinstance(bbox, list) or len(bbox) != 4:
            raise datagen.SpecException(
                'Bounding box must be list of size 4 with format: [min Longitude, min Latitude, max Longitude, max Latitude]')
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
