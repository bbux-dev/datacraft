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
