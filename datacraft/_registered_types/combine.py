"""module for combine type datacraft registry functions"""
import json
import logging

import datacraft
from . import common
from . import schemas

_log = logging.getLogger(__name__)
_COMBINE_KEY = 'combine'
_COMBINE_LIST_KEY = 'combine-list'
_COMBINE_EXAMPLE = {
    "name": {
        "type": "combine",
        "refs": ["first", "last"],
        "config": {
            "join_with": " "
        }
    },
    "refs": {
        "first": {
            "type": "values",
            "data": ["zebra", "hedgehog", "llama", "flamingo"]
        },
        "last": {
            "type": "values",
            "data": ["jones", "smith", "williams"]
        }
    }
}
_COMBINE_LIST_EXAMPLE = {
    "full_name": {
        "type": "combine-list",
        "refs": [
            ["first", "last"],
            ["first", "middle", "last"],
            ["first", "middle_initial", "last"]
        ],
        "config": {
            "join_with": " "
        }
    },
    "refs": {
        "first": {
            "type": "values",
            "data": ["zebra", "hedgehog", "llama", "flamingo"]
        },
        "last": {
            "type": "values",
            "data": ["jones", "smith", "williams"]
        },
        "middle": {
            "type": "values",
            "data": ["cloud", "sage", "river"]
        },
        "middle_initial": {
            "type": "values",
            "data": {"a": 0.3, "m": 0.3, "j": 0.1, "l": 0.1, "e": 0.1, "w": 0.1}
        }
    }
}


@datacraft.registry.schemas(_COMBINE_KEY)
def _get_combine_schema():
    """ get the schema for the combine type """
    return schemas.load(_COMBINE_KEY)


@datacraft.registry.schemas(_COMBINE_LIST_KEY)
def _get_combine_list_schema():
    """ get the schema for the combine_list type """
    return schemas.load(_COMBINE_LIST_KEY)


@datacraft.registry.types(_COMBINE_KEY)
def _configure_combine_supplier(field_spec, loader):
    """ configures supplier for combine type """
    if 'refs' not in field_spec and 'fields' not in field_spec:
        raise datacraft.SpecException(f'Must define one of fields or refs. {json.dumps(field_spec)}')

    if 'refs' in field_spec:
        supplier = _load_combine_from_refs(field_spec, loader)
    else:
        supplier = _load_combine_from_fields(field_spec, loader)
    return supplier


@datacraft.registry.types(_COMBINE_LIST_KEY)
def _configure_combine_list_supplier(field_spec, loader):
    """ configures supplier for combine-list type """
    if 'refs' not in field_spec:
        raise datacraft.SpecException(f'Must define refs for combine-list type. {json.dumps(field_spec)}')

    refs_list = field_spec['refs']
    if len(refs_list) < 1 or not isinstance(refs_list[0], list):
        raise datacraft.SpecException(
            f'refs pointer must be list of lists: i.e [["ONE", "TWO"]]. {json.dumps(field_spec)}')

    suppliers_list = []
    for ref in refs_list:
        spec = dict(field_spec)
        spec['refs'] = ref
        suppliers_list.append(_load_combine_from_refs(spec, loader))
    return datacraft.suppliers.from_list_of_suppliers(suppliers_list, True)


def _load_combine_from_refs(combine_field_spec, loader):
    """ loads the combine type from a set of refs """
    keys = combine_field_spec.get('refs')
    return _load_combine(combine_field_spec, keys, loader)


def _load_combine_from_fields(combine_field_spec, loader):
    """ load the combine type from a set of field names """
    keys = combine_field_spec.get('fields')
    return _load_combine(combine_field_spec, keys, loader)


def _load_combine(combine_field_spec, keys, loader):
    """ create the combine supplier for the types from the given keys """
    to_combine = []
    for key in keys:
        supplier = loader.get(key)
        to_combine.append(supplier)
    config = combine_field_spec.get('config', {})
    as_list = config.get('as_list', datacraft.registries.get_default('combine_as_list'))
    joiner = config.get('join_with', datacraft.registries.get_default('combine_join_with'))
    return datacraft.suppliers.combine(to_combine, joiner, as_list)


@datacraft.registry.usage(_COMBINE_KEY)
def _example_combine_usage():
    return common.standard_example_usage(_COMBINE_EXAMPLE, 3)


@datacraft.registry.usage(_COMBINE_LIST_KEY)
def _example_combine_list_usage():
    return common.standard_example_usage(_COMBINE_LIST_EXAMPLE, 3)
