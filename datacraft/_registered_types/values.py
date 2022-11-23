"""module for values type datacraft registry functions"""
import logging

import datacraft
from . import common
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


@datacraft.registry.usage(_VALUES_KEY)
def _example_values_usage():
    example = {
        "field_constant": {"type": "values", "data": 42},
        "field_list": {"type": "values", "data": [1, 2, 3, 5, 8, 13, None]},
        "field_weighted": {"type": "values", "data": {"200": 0.6, "404": 0.1, "303": 0.3}},
        "field_weighted_with_null": {"type": "values", "data": {"200": 0.5, "404": 0.1, "303": 0.3, "_NULL_": 0.1}},
        "field_weighted_booleans": {"_TRUE_": 0.3, "_FALSE_": 0.6, "_NIL_": 0.1}
    }
    return common.standard_example_usage(example, 1, pretty=True)
