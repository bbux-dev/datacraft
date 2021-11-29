"""
Module to support combine type
"""
import json

from .exceptions import SpecException
from .supplier.combine import combine_supplier
from . import types, schemas, suppliers

COMBINE_KEY = 'combine'
COMBINE_LIST_KEY = 'combine-list'


@types.registry.schemas(COMBINE_KEY)
def _get_combine_schema():
    """ get the schema for the combine type """
    return schemas.load(COMBINE_KEY)


@types.registry.schemas(COMBINE_LIST_KEY)
def _get_combine_list_schema():
    """ get the schema for the combine_list type """
    return schemas.load(COMBINE_LIST_KEY)


@types.registry.types(COMBINE_KEY)
def _configure_combine_supplier(field_spec, loader):
    """ configures supplier for combine type """
    if 'refs' not in field_spec and 'fields' not in field_spec:
        raise SpecException('Must define one of fields or refs. %s' % json.dumps(field_spec))

    if 'refs' in field_spec:
        supplier = _load_from_refs(field_spec, loader)
    else:
        supplier = _load_from_fields(field_spec, loader)
    return supplier


@types.registry.types(COMBINE_LIST_KEY)
def _configure_combine_list_supplier(field_spec, loader):
    """ configures supplier for combine-list type """
    if 'refs' not in field_spec:
        raise SpecException('Must define refs for combine-list type. %s' % json.dumps(field_spec))

    refs_list = field_spec['refs']
    if len(refs_list) < 1 or not isinstance(refs_list[0], list):
        raise SpecException(
            'refs pointer must be list of lists: i.e [["ONE", "TWO"]]. %s' % json.dumps(field_spec))

    suppliers_list = []
    for ref in refs_list:
        spec = dict(field_spec)
        spec['refs'] = ref
        suppliers_list.append(_load_from_refs(spec, loader))
    return suppliers.from_list_of_suppliers(suppliers_list, True)


def _load_from_refs(combine_field_spec, loader):
    """ loads the combine type from a set of refs """
    keys = combine_field_spec.get('refs')
    return _load(combine_field_spec, keys, loader)


def _load_from_fields(combine_field_spec, loader):
    """ load the combine type from a set of field names """
    keys = combine_field_spec.get('fields')
    return _load(combine_field_spec, keys, loader)


def _load(combine_field_spec, keys, loader):
    """ create the combine supplier for the types from the given keys """
    to_combine = []
    for key in keys:
        supplier = loader.get(key)
        to_combine.append(supplier)
    config = combine_field_spec.get('config', {})
    as_list = config.get('as_list', types.get_default('combine_as_list'))
    joiner = config.get('join_with', types.get_default('combine_join_with'))
    return combine_supplier(to_combine, as_list, joiner)
