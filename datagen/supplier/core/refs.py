"""
Module for ref type
"""
import json
import datagen


@datagen.registry.schemas('ref')
def _get_ref_schema():
    return datagen.schemas.load('ref')


@datagen.registry.types('ref')
def _configure_ref_supplier(field_spec: dict, loader: datagen.Loader):
    """ configures supplier for ref type """
    key = None
    if 'data' in field_spec:
        key = field_spec.get('data')
    if 'ref' in field_spec:
        key = field_spec.get('ref')
    if key is None:
        raise datagen.SpecException('No key found for spec: ' + json.dumps(field_spec))
    return loader.get(key)
