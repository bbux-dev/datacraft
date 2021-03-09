"""
select_list_subset handler builds a select_list_subset supplier from the provided spec

A select list subset spec is used to select multiple values from a list to use as the value for a field.

The select_list_subset Field Spec structure is:
```json
{
  "<field name>": {
    "type": "select_list_subset",
    "config": {
      "mean": N,
      "stddev": N,
      "min": N,
      "max": N,
      "join_with": "<delimiter to join with>"
     },
    "data": ["data", "to", "secect", "from"],
    OR
    "ref": "REF_WITH_DATA_AS_LIST"
  }
}
```
"""
import json

import dataspec
from dataspec.exceptions import SpecException
from dataspec.supplier.list_sampler import ListSampler
from dataspec.utils import load_config


@dataspec.registry.types('select_list_subset')
def configure_supplier(field_spec, loader):
    """ configures supplier for select_list_subset type """
    config = load_config(field_spec, loader)
    if config is None or 'mean' not in config:
        raise SpecException('Config with mean defined must be provided: %s' % json.dumps(field_spec))
    if 'ref' in field_spec and 'data' in field_spec:
        raise SpecException('Only one of "data" or "ref" can be provided for: %s' % json.dumps(field_spec))

    if 'ref' in field_spec:
        ref_name = field_spec.get('ref')
        field_spec = loader.refs.get(ref_name)
        if field_spec is None:
            raise SpecException('No ref with name %s found: %s' % (ref_name, json.dumps(field_spec)))

        if 'data' in field_spec:
            data = field_spec.get('data')
        else:
            data = field_spec

    if 'data' in field_spec:
        data = field_spec.get('data')

    return ListSampler(data, config)
