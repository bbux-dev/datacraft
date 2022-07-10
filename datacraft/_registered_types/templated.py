"""module for templated type datacraft registry functions"""
import json
import logging

import datacraft
from . import common
from . import schemas
from .common import build_suppliers_map

_log = logging.getLogger(__name__)
_TEMPLATED_KEY = 'templated'


@datacraft.registry.schemas(_TEMPLATED_KEY)
def _templated_schema():
    return schemas.load(_TEMPLATED_KEY)


@datacraft.registry.types(_TEMPLATED_KEY)
def _configure_templated_type(field_spec, loader):
    if 'data' not in field_spec:
        raise datacraft.SpecException(f'data is required field for templated specs: {json.dumps(field_spec)}')
    suppliers_map = build_suppliers_map(field_spec, loader)

    return datacraft.suppliers.templated(suppliers_map, field_spec.get('data', None))


@datacraft.registry.usage(_TEMPLATED_KEY)
def _example_templated_usage():
    example = {
        "user_agent": {
            "type": "templated",
            "data": "Mozilla/5.0 ({{ system }}) {{ platform }}",
            "refs": ["system", "platform"],
        },
        "refs": {
            "system": {
                "type": "values",
                "data": [
                    "Windows NT 6.1; Win64; x64; rv:47.0",
                    "Macintosh; Intel Mac OS X x.y; rv:42.0"
                ]
            },
            "platform": {
                "type": "values",
                "data": ["Gecko/20100101 Firefox/47.0", "Gecko/20100101 Firefox/42.0"]
            }
        }
    }
    return common.standard_example_usage(example, 1, pretty=True)
