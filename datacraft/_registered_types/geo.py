"""module for geo type datacraft registry functions"""
import logging

import datacraft
from . import common
from . import schemas

_log = logging.getLogger(__name__)
_GEO_LAT_KEY = 'geo.lat'
_GEO_LONG_KEY = 'geo.long'
_GEO_PAIR_KEY = 'geo.pair'


@datacraft.registry.schemas(_GEO_LAT_KEY)
def _get_geo_lat_schema():
    """ schema for geo.lat type """
    return schemas.load(_GEO_LAT_KEY)


@datacraft.registry.schemas(_GEO_LONG_KEY)
def _get_geo_long_schema():
    """ schema for geo.long type """
    return schemas.load(_GEO_LONG_KEY)


@datacraft.registry.schemas(_GEO_PAIR_KEY)
def _get_geo_pair_schema():
    """ schema for geo.pair type """
    return schemas.load(_GEO_PAIR_KEY)


@datacraft.registry.types(_GEO_LAT_KEY)
def _configure_geo_lat(field_spec, loader):
    """ configures value supplier for geo.lat type """
    config = datacraft.utils.load_config(field_spec, loader)
    return datacraft.suppliers.geo_lat(**config)


@datacraft.registry.types(_GEO_LONG_KEY)
def _configure_geo_long(field_spec, loader):
    """ configures value supplier for geo.long type """
    config = datacraft.utils.load_config(field_spec, loader)
    return datacraft.suppliers.geo_long(**config)


@datacraft.registry.types(_GEO_PAIR_KEY)
def _configure_geo_pair(field_spec, loader):
    """ configures value supplier for geo.pair type """
    config = datacraft.utils.load_config(field_spec, loader)
    return datacraft.suppliers.geo_pair(**config)


@datacraft.registry.usage(_GEO_LAT_KEY)
def _get_geo_lat_usage():
    """ usage for geo.lat type """
    example = {
        "lat": {
            "type": "geo.lat",
            "config": {
                "start_lat": -45.0,
                "end_lat": 45.0
            }
        }
    }
    return common.standard_example_usage(example, 3)


@datacraft.registry.usage(_GEO_LONG_KEY)
def _get_geo_long_usage():
    """ usage for geo.long type """
    example = {
        "long": {
            "type": "geo.long",
            "config": {
                "start_long": -45.0,
                "end_long": 45.0
            }
        }
    }
    return common.standard_example_usage(example, 3)


@datacraft.registry.usage(_GEO_PAIR_KEY)
def _get_geo_pair_usage():
    """ usage for geo.pair type """
    example = {
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
    return common.standard_example_usage(example, 3)
