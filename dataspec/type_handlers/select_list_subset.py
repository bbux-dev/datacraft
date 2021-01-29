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
import math
import random
import sys
from random import gauss

import dataspec
# when doing explicit import of SpecExcption get:
# cannot import name 'SpecException' from partially initialized module 'dataspec'
from dataspec.utils import load_config


@dataspec.registry.types('select_list_subset')
def configure_supplier(field_spec, loader):
    config = load_config(field_spec, loader)
    if config is None or 'mean' not in config:
        raise dataspec.SpecException('Config with mean defined must be provided: %s' % json.dumps(field_spec))
    if 'ref' in field_spec and 'data' in field_spec:
        raise dataspec.SpecException('Only one of "data" or "ref" can be provided for: %s' % json.dumps(field_spec))

    if 'ref' in field_spec:
        ref_name = field_spec.get('ref')
        field_spec = loader.refs.get(ref_name)
        if field_spec is None:
            raise dataspec.SpecException('No ref with name %s found: %s' % (ref_name, json.dumps(field_spec)))

        if 'data' in field_spec:
            data = field_spec.get('data')
        else:
            data = field_spec

    if 'data' in field_spec:
        data = field_spec.get('data')

    return SelectListSupplier(data, config)


class SelectListSupplier:
    def __init__(self, data, config):
        self.values = data
        self.mean = float(config.get('mean'))
        self.stddev = config.get('stddev', 0)
        self.min = int(config.get('min', 1))
        self.max = int(config.get('max', sys.maxsize))
        self.join_with = config.get('join_with', ' ')

    def next(self, _):
        count = math.ceil(gauss(self.mean, self.stddev))
        if count <= 0:
            count = 1
        if count > self.max:
            count = self.max
        if count < self.min:
            count = self.min
        # last check, cant sample more than exists
        if count > len(self.values):
            count = len(self.values)

        data = random.sample(self.values, count)
        return self.join_with.join(data)
