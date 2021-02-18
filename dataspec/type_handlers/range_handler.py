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
import dataspec.casters as casters
from dataspec.utils import load_config, get_caster


@dataspec.registry.types('range')
def configure_range_supplier(field_spec, _):
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


@dataspec.registry.types('rand_range')
def configure_rand_range_supplier(field_spec, loader):
    """ configures the random range value supplier """
    if 'data' not in field_spec:
        raise dataspec.SpecException('No data element defined for: %s' % json.dumps(field_spec))
    data = field_spec.get('data')
    config = load_config(field_spec, loader)
    if not isinstance(data, list) or len(data) == 0:
        raise dataspec.SpecException('rand_range specs require data as array with at least one element: %s' % json.dumps(field_spec))
    start = 0
    if len(data) == 1:
        end = data[0]
    if len(data) == 2:
        start = data[0]
        end = data[1]
    precision = None
    if len(data) > 2:
        precision = data[2]
    # config overrides third data element if specified
    precision = config.get('precision', precision)
    return suppliers.random_range(start, end, precision)


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
