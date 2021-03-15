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
from dataspec import registry, suppliers


@registry.types('weightedref')
def configure_supplier(parent_field_spec, loader):
    """ configures supplier for weighted ref specs """
    key_supplier = suppliers.values(parent_field_spec)
    values_map = {}
    for key in parent_field_spec['data'].keys():
        supplier = loader.get(key)
        values_map[key] = supplier
    return suppliers.weighted_ref(key_supplier, values_map)
