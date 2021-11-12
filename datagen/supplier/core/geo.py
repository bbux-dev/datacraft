"""
There are three main geo types: ``geo.lat``, ``geo.long``, and ``geo.pair``. The defaults will create decimal string
values in the valid ranges: -90 to 90 for latitude and -180 to 180 for longitude. You can bound the ranges in several
ways. The first is with the start_lat, end_lat, start_long, end_long config params. These will set the individual
bounds for each of the segments. You can use one or more of them. The other mechanism is by defining a bbox array
which consists of the lower left geo point and the upper right one.

.. list-table::
   :header-rows: 1

   * - type
     - param
     - description
   * - all
     - precision
     - number of decimal places for lat or long, default is 4
   * -
     - bbox
     - array of [min Longitude, min Latitude, max Longitude, max Latitude]
   * - geo.lat
     - start_lat
     - lower bound for latitude
   * -
     - end_lat
     - upper bound for latitude
   * - geo.long
     - start_long
     - lower bound for longitude
   * -
     - end_long
     - upper bound for longitude
   * - geo.pair
     - join_with
     - delimiter to join long and lat with, default is comma
   * -
     - as_list
     - One of yes, true, or on if the pair should be returned as a list instead of as a joined string
   * -
     - lat_first
     - if latitude should be first in the generated pair, default is longitude first
   * -
     - start_lat
     - lower bound for latitude
   * -
     - end_lat
     - upper bound for latitude
   * -
     - start_long
     - lower bound for longitude
   * -
     - end_long
     - upper bound for longitude


Prototype:

.. code-block:: python

    {
      "<field name>": {
        "type": "geo.lat",
        or
        "type": "geo.long",
        or
        "type": "geo.pair",
        "config": {
          "key": Any
        }
      }
    }

Examples:

.. code-block:: json

    {
      "egypt": {
        "type": "geo.pair",
        "config": {
          "bbox": [
            31.33134,
            22.03795,
            34.19295,
            25.00562
          ],
          "precision": 3
        }
      }
    }
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
        raise datagen.SpecException(f'precision for geo should be valid integer >= 0: {json.dumps(spec)}')
    start, end = _get_start_end(config, default_start, default_end, suffix)
    range_supplier = datagen.suppliers.random_range(start, end, precision)
    return GeoSupplier(range_supplier)


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
