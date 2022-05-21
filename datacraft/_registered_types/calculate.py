import json
import logging

import datacraft
from . import schemas
from .common import _build_suppliers_map

_log = logging.getLogger(__name__)
_CALCULATE_KEY = 'calculate'


@datacraft.registry.schemas(_CALCULATE_KEY)
def _calculate_schema():
    """ get the schema for the calculate type """
    return schemas.load(_CALCULATE_KEY)


@datacraft.registry.types(_CALCULATE_KEY)
def _configure_calculate_supplier(field_spec: dict, loader: datacraft.Loader):
    """ configures supplier for calculate type """

    formula = field_spec.get('formula')
    if formula is None:
        raise datacraft.SpecException('Must define formula for calculate type. %s' % json.dumps(field_spec))

    suppliers_map = _build_suppliers_map(field_spec, loader)

    return datacraft.suppliers.calculate(suppliers_map=suppliers_map, formula=formula)
