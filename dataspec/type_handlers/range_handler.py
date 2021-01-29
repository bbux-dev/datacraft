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
import decimal
import dataspec
import dataspec.suppliers as suppliers


@dataspec.registry.types('range')
def configure_supplier(field_spec, _):
    """ configures the range value supplier """
    if 'data' not in field_spec:
        raise dataspec.SpecException('No data element defined for: %s' % json.dumps(field_spec))

    data = field_spec.get('data')
    if not isinstance(data, list) or len(data) < 2:
        raise dataspec.SpecException(
            'data element for ranges type must be list with at least two elements: %s' % json.dumps(field_spec))
    start = data[0]
    # default for built in range function is exclusive end, we want to default to inclusive as this is the
    # more intuitive behavior
    end = data[1] + 1
    if not end > start:
        raise dataspec.SpecException('end element must be larger than start: %s' % json.dumps(field_spec))
    if len(data) == 2:
        step = 1
    else:
        step = data[2]
    if _any_is_float(data):
        range_values = list(float_range(float(start), float(end), float(step)))
    else:
        range_values = list(range(start, end, step))
    return suppliers.values(range_values)


def _any_is_float(data):
    """ are any of the items floats """
    for item in data:
        if isinstance(item, float):
            return True
    return False


def float_range(start, stop, step):
    """
    Fancy foot work to support floating point ranges due to rounding errors with the way floating point numbers are stored
    """
    # attempt to defeat some rounding errors prevalent in python
    current = decimal.Decimal(str(start))
    dstop = decimal.Decimal(str(stop))
    dstep = decimal.Decimal(str(step))
    while current < dstop:
        # inefficient?
        yield float(str(current))
        current = current + dstep
