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

import datagen


@datagen.registry.types('select_list_subset')
def configure_supplier(field_spec, loader):
    """ configures supplier for select_list_subset type """
    config = datagen.utils.load_config(field_spec, loader)
    if config is None or ('mean' not in config and 'count' not in config):
        raise datagen.SpecException('Config with mean or count defined must be provided: %s' % json.dumps(field_spec))
    if 'ref' in field_spec and 'data' in field_spec:
        raise datagen.SpecException('Only one of "data" or "ref" can be provided for: %s' % json.dumps(field_spec))

    if 'ref' in field_spec:
        ref_name = field_spec.get('ref')
        field_spec = loader.get_ref_spec(ref_name)
        if field_spec is None:
            raise datagen.SpecException('No ref with name %s found: %s' % (ref_name, json.dumps(field_spec)))

        if 'data' in field_spec:
            data = field_spec.get('data')
        else:
            data = field_spec

    if 'data' in field_spec:
        data = field_spec.get('data')
    if datagen.utils.any_key_exists(config, ['mean', 'stddev']):
        return datagen.suppliers.list_stat_sampler(data, config)
    return datagen.suppliers.list_count_sampler(data, config)
