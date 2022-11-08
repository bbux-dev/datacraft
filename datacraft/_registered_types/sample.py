"""module for sample type datacraft registry functions"""
import json
import logging

import datacraft
from . import common
from . import schemas

_log = logging.getLogger(__name__)
_SAMPLE_KEY = 'sample'
# legacy alias
_SELECT_LIST_SUBSET_KEY = 'select_list_subset'


@datacraft.registry.schemas(_SAMPLE_KEY)
def _sample_schema():
    """ schema for sample alias type """
    return schemas.load(_SAMPLE_KEY)


@datacraft.registry.schemas(_SELECT_LIST_SUBSET_KEY)
def _select_list_subset_schema():
    """ schema for sample type """
    schema = schemas.load(_SAMPLE_KEY)
    schema['properties']['type']['pattern'] = f'^{_SELECT_LIST_SUBSET_KEY}$'
    return schema


@datacraft.registry.types(_SAMPLE_KEY)
@datacraft.registry.types(_SELECT_LIST_SUBSET_KEY)
def _configure_select_list_subset_supplier(field_spec, loader):
    """ configures supplier for sample type """
    config = datacraft.utils.load_config(field_spec, loader)
    data = None
    if config is None or ('mean' not in config and 'count' not in config):
        raise datacraft.SpecException(f'Config with mean or count defined must be provided: {json.dumps(field_spec)}')
    if 'ref' in field_spec and 'data' in field_spec:
        raise datacraft.SpecException(f'Only one of "data" or "ref" can be provided for:{json.dumps(field_spec)}')

    if 'ref' in field_spec:
        ref_name = field_spec.get('ref')
        field_spec = loader.get_ref(ref_name)
        if field_spec is None:
            raise datacraft.SpecException(f'No ref with name %s found: {ref_name}, {json.dumps(field_spec)}')

        if 'data' in field_spec:
            data = field_spec.get('data')
        else:
            data = field_spec
    elif 'data' in field_spec:
        data = field_spec.get('data')
    if data is None:
        raise datacraft.SpecException(
            'Unable to identify data for ' + _SAMPLE_KEY + ' for spec: ' + json.dumps(field_spec))
    return datacraft.suppliers.sample(data, **config)


@datacraft.registry.usage(_SELECT_LIST_SUBSET_KEY)
def _example_select_list_subset_usage():
    return "alias for " + _SAMPLE_KEY


@datacraft.registry.usage(_SAMPLE_KEY)
def _example_sample_usage():
    example = {
        "ingredients": {
            "type": _SAMPLE_KEY,
            "data": ["onions", "mushrooms", "garlic", "bell peppers", "spinach", "potatoes", "carrots"],
            "config": {
                "mean": 3,
                "stddev": 1,
                "min": 2,
                "max": 4,
                "join_with": ", "
            }
        }
    }
    return common.standard_example_usage(example, 3)
