import json
import logging

from . import common
import datacraft
from . import schemas

_log = logging.getLogger(__name__)
_UUID_KEY = 'uuid'


@datacraft.registry.schemas(_UUID_KEY)
def _get_uuid_schema():
    """ get the schema for uuid type """
    return schemas.load(_UUID_KEY)


@datacraft.registry.types(_UUID_KEY)
def _configure_uuid_supplier(field_spec, loader):
    """ configure the supplier for uuid types """
    config = datacraft.utils.load_config(field_spec, loader)
    variant = int(config.get('variant', datacraft.registries.get_default('uuid_variant')))

    if variant not in [1, 3, 4, 5]:
        raise datacraft.SpecException('Invalid variant for: ' + json.dumps(field_spec))
    return datacraft.suppliers.uuid(variant)
