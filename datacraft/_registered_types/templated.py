import json
import logging

from . import common
import datacraft
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
