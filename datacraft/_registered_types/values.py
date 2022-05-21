import logging

import datacraft
from . import schemas

_log = logging.getLogger(__name__)
_VALUES_KEY = 'values'


@datacraft.registry.schemas(_VALUES_KEY)
def _get_values_schema():
    """ returns the values schema """
    return schemas.load(_VALUES_KEY)


@datacraft.registry.types(_VALUES_KEY)
def _handle_values_type(spec, loader):
    """ handles values types """
    config = datacraft.utils.load_config(spec, loader)
    return datacraft.suppliers.values(spec, **config)
