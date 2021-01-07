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
from datamaker import suppliers
from datamaker import SpecException


def configure_supplier(data_spec, loader):
    config = data_spec.get('config')
    if config is None or 'mean' not in config:
        raise SpecException('Config with mean defined must be provided: %s' % json.dumps(data_spec))
    if 'ref' in data_spec and 'data' in data_spec:
        raise SpecException('Only one of "data" or "ref" can be provided for: %s' % json.dumps(data_spec))

    if 'ref' in data_spec:
        ref_name = data_spec.get('ref')
        field_spec = loader.refs.get(ref_name)
        if field_spec is None:
            raise SpecException('No ref with name %s found: %s' % (ref_name, json.dumps(data_spec)))

        if 'data' in field_spec:
            data = field_spec.get('data')
        else:
            data = field_spec

    if 'data' in data_spec:
        data = data_spec.get('data')

    return suppliers.select_list_subset(data, config)
