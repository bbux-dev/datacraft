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
import json
from datamaker import suppliers
from datamaker import SpecException


def configure_supplier(parent_field_spec, loader):
    key_supplier = suppliers.values(parent_field_spec)
    values_map = {}
    for key in parent_field_spec['data'].keys():
        field_spec = loader.refs.get(key)
        supplier = loader.get_from_spec(field_spec)
        if supplier is None:
            raise SpecException("Unable to get supplier for ref key: %s, spec: %s" % (key, json.dumps(field_spec)))
        values_map[key] = supplier
    return suppliers.weighted_ref(key_supplier, values_map)
