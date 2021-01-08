"""
Configures a supplier to provide a range of integers. Range is are inclusive for start and end

Range Spec format:

{
  "range_field": {
    "type": "range",
    "data": [start, stop, optional step]
  }
}
"""
import json
import datamaker
import datamaker.suppliers as suppliers


@datamaker.registry.types('range')
def configure_supplier(field_spec, _):
    if 'data' not in field_spec:
        raise datamaker.SpecException('No data element defined for: %s' % json.dumps(field_spec))

    data = field_spec.get('data')
    if not isinstance(data, list) or len(data) < 2:
        raise datamaker.SpecException('data element for ranges type must be list with at least two elements: %s' % json.dumps(field_spec))
    start = data[0]
    # default for built in range function is exclusive end, we want to default to inclusive as this is the
    # more intuitive behavior
    end = data[1] + 1
    if not end > start:
        raise datamaker.SpecException('end element must be larger than start: %s' % json.dumps(field_spec))
    if len(data) == 2:
        range_values = list(range(start, end))
    else:
        range_values = list(range(start, end, data[2]))
    return suppliers.values(range_values)
