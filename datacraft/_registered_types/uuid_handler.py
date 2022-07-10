"""module for uuid_handler type datacraft registry functions"""
import json
import logging

import datacraft

from . import common
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


@datacraft.registry.usage(_UUID_KEY)
def _example_uuid_usage():
    example = {
        "id": {
            "type": _UUID_KEY,
        },
        "id_variant3": {
            "type": _UUID_KEY,
            "config": {
                "variant": 3
            }
        }
    }
    return common.standard_example_usage(example, 3, pretty=True)
