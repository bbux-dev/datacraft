"""
This module handles the weightedref type.

A weighted ref spec is used to select the values from a set of refs in a weighted fashion.

The weightedref Field Spec structure is:
{
  "<field name>": {
    "type": "weightedref",
    "data": { "valid_ref_1": 0.N, "valid_ref_2": 0.N, ... }
  }
}
"""
from dataspec import registry, suppliers, utils


@registry.types('weightedref')
def configure_supplier(parent_field_spec, loader):
    """ configures supplier for weighted ref specs """
    config = utils.load_config(parent_field_spec, loader)
    data = parent_field_spec['data']
    key_supplier = suppliers.values(data)
    values_map = {}
    for key in data.keys():
        supplier = loader.get(key)
        values_map[key] = supplier
    supplier = suppliers.weighted_ref(key_supplier, values_map)
    if 'count' in config:
        return suppliers.array_supplier(supplier, config.get('count', 1))
    return supplier
