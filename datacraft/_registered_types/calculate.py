"""module for calculate type datacraft registry functions"""
import json
import logging

import datacraft
import datacraft.spec_formatters
from . import common
from . import schemas
from .common import build_suppliers_map

_log = logging.getLogger(__name__)
_CALCULATE_KEY = 'calculate'
_EXAMPLE_SPEC = {
    "height_in": [60, 70, 80, 90],
    "height_cm": {
        "type": "calculate",
        "fields": ["height_in"],
        "formula": "{{ height_in }} * 2.54"
    }
}


@datacraft.registry.schemas(_CALCULATE_KEY)
def _calculate_schema():
    """ get the schema for the calculate type """
    return schemas.load(_CALCULATE_KEY)


@datacraft.registry.types(_CALCULATE_KEY)
def _configure_calculate_supplier(field_spec: dict, loader: datacraft.Loader):
    """ configures supplier for calculate type """

    formula = field_spec.get('formula')
    if formula is None:
        raise datacraft.SpecException(f'Must define formula for calculate type. {json.dumps(field_spec)}')

    suppliers_map = build_suppliers_map(field_spec, loader)

    return datacraft.suppliers.calculate(suppliers_map=suppliers_map, formula=formula)


@datacraft.registry.usage(_CALCULATE_KEY)
def _example_usage():
    return common.standard_example_usage(_EXAMPLE_SPEC, 3)
