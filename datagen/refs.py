"""
Module for ref type
"""
import json

from . import types, schemas, suppliers, utils
from .exceptions import SpecException
from .loader import Loader
from .supplier.refs import weighted_ref_supplier

_WEIGHTED_REF_KEY = 'weighted_ref'


@types.registry.schemas('ref')
def _get_ref_schema():
    return schemas.load('ref')


@types.registry.types('ref')
def _configure_ref_supplier(field_spec: dict, loader: Loader):
    """ configures supplier for ref type """
    key = None
    if 'data' in field_spec:
        key = field_spec.get('data')
    if 'ref' in field_spec:
        key = field_spec.get('ref')
    if key is None:
        raise SpecException('No key found for spec: ' + json.dumps(field_spec))
    return loader.get(key)


@types.registry.schemas(_WEIGHTED_REF_KEY)
def _weighted_ref_schema():
    return schemas.load(_WEIGHTED_REF_KEY)


@types.registry.types(_WEIGHTED_REF_KEY)
def _configure_supplier(parent_field_spec, loader):
    """ configures supplier for weighted ref specs """
    config = utils.load_config(parent_field_spec, loader)
    data = parent_field_spec['data']
    key_supplier = suppliers.values(data)
    values_map = {}
    for key in data.keys():
        supplier = loader.get(key)
        values_map[key] = supplier
    supplier = weighted_ref_supplier(key_supplier, values_map)
    if 'count' in config:
        return suppliers.array_supplier(supplier, config)
    return supplier
