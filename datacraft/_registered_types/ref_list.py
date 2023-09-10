"""module for ref_lists type datacraft registry functions"""
import json
import logging

import datacraft
from . import common
from . import schemas

_log = logging.getLogger(__name__)
_REF_LIST_KEY = 'ref_list'


@datacraft.registry.schemas(_REF_LIST_KEY)
def _get_ref_list_schema():
    """ schema for ref_list type """
    return schemas.load(_REF_LIST_KEY)


@datacraft.registry.types(_REF_LIST_KEY)
def _configure_ref_list_supplier(field_spec: dict, loader: datacraft.Loader):
    """ configures supplier for ref_list type """
    keys = None
    if 'data' in field_spec:
        keys = field_spec.get('data')
    if 'refs' in field_spec:
        keys = field_spec.get('refs')
    if keys is None:
        raise datacraft.SpecException('No keys found for spec: ' + json.dumps(field_spec))
    supplier_list = [loader.get(k) for k in keys]
    return datacraft.suppliers.combine_supplier(supplier_list, as_list=True)


@datacraft.registry.usage(_REF_LIST_KEY)
def _example_ref_list_usage():
    example = {
        "location": {
            "type": "ref_list",
            "refs": [
                "lat",
                "long",
                "altitude"
            ]
        },
        "refs": {
            "lat:geo.lat": {},
            "long:geo.long": {},
            "altitude:rand_int_range": [5000, 10000]
        }
    }

    return common.standard_example_usage(example, 3)
