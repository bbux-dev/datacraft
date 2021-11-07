"""
There are two main range types sequential and random.  A sequential range is
specified using the ``range`` type.  A random one uses the ``rand_range`` type.

range
-----

Prototype:

.. code-block:: python

    {
      "<field name>": {
        "type": "range",
        "data": [<start>, <end>, <step> (optional)],
        or
        "data": [
          [<start>, <end>, <step> (optional)],
          [<start>, <end>, <step> (optional)],
          ...
          [<start>, <end>, <step> (optional)],
        ],
      }
    }

    start: (Union[int, float]) - start of range
    end: (Union[int, float]) - end of range
    step: (Union[int, float]) - step for range, default is 1

Examples:

.. code-block:: json

    {
      "zero_to_ten_step_half": {
        "type": "range",
        "data": [0, 10, 0.5]
      }
    },
    {
      "range_shorthand1:range": {
        "data": [0, 10, 0.5]
      }
    },
    {"range_shorthand2:range": [0, 10, 0.5]},

rand_range
----------

Prototype:

.. code-block:: python

    {
      "<field name>": {
        "type": "rand_range",
        "data": [<upper>],
        or
        "data": [<lower>, <upper>],
        or
        "data": [<lower>, <upper>, <precision> (optional)]
      }
    }

    upper: (Union[int, float]) - upper limit of random range
    lower: (Union[int, float]) - lower limit of random range
    precision: (int) - Number of digits after decimal point
"""
import decimal
import json
import math

import datagen

RANGE_KEY = 'range'
RAND_RANGE_KEY = 'rand_range'


@datagen.registry.schemas(RANGE_KEY)
def _get_range_schema():
    """ schema for range type """
    return datagen.schemas.load(RANGE_KEY)


@datagen.registry.schemas(RAND_RANGE_KEY)
def _get_rand_range_schema():
    """ schema for rand range type """
    # This shares a schema with range
    return datagen.schemas.load(RANGE_KEY)


@datagen.registry.types(RANGE_KEY)
def _configure_range_supplier(field_spec, _):
    """ configures the range value supplier """
    if 'data' not in field_spec:
        raise datagen.SpecException('No data element defined for: %s' % json.dumps(field_spec))

    data = field_spec.get('data')
    if not isinstance(data, list) or len(data) < 2:
        raise datagen.SpecException(
            'data element for ranges type must be list with at least two elements: %s' % json.dumps(field_spec))
    # we have the nested case
    if isinstance(data[0], list):
        suppliers_list = [_configure_supplier_for_data(field_spec, subdata) for subdata in data]
        return datagen.suppliers.from_list_of_suppliers(suppliers_list, True)
    return _configure_supplier_for_data(field_spec, data)


def _configure_supplier_for_data(field_spec, data):
    """ configures the supplier based on the range data supplied """
    start = data[0]
    # default for built in range function is exclusive end, we want to default to inclusive as this is the
    # more intuitive behavior
    end = data[1] + 1
    if not end > start:
        raise datagen.SpecException('end element must be larger than start: %s' % json.dumps(field_spec))
    if len(data) == 2:
        step = 1
    else:
        step = data[2]
    if _any_is_float(data):
        config = field_spec.get('config', {})
        precision = config.get('precision', None)
        if precision and not str(precision).isnumeric():
            raise datagen.SpecException(f'precision must be valid integer {json.dumps(field_spec)}')
        range_values = list(float_range(float(start), float(end), float(step), precision))
    else:
        range_values = list(range(start, end, step))
    return datagen.suppliers.values(range_values)


@datagen.registry.types(RAND_RANGE_KEY)
def _configure_rand_range_supplier(field_spec, loader):
    """ configures the random range value supplier """
    if 'data' not in field_spec:
        raise datagen.SpecException('No data element defined for: %s' % json.dumps(field_spec))
    data = field_spec.get('data')
    config = datagen.utils.load_config(field_spec, loader)
    if not isinstance(data, list) or len(data) == 0:
        raise datagen.SpecException(
            'rand_range specs require data as array with at least one element: %s' % json.dumps(field_spec))
    start = 0
    if len(data) == 1:
        end = data[0]
    if len(data) >= 2:
        start = data[0]
        end = data[1]
    precision = None
    if len(data) > 2:
        precision = data[2]
    # config overrides third data element if specified
    precision = config.get('precision', precision)
    return datagen.suppliers.random_range(start, end, precision)


def _any_is_float(data):
    """ are any of the items floats """
    for item in data:
        if isinstance(item, float):
            return True
    return False


def float_range(start: float,
                stop: float,
                step: float,
                precision=None):
    """
    Fancy foot work to support floating point ranges due to rounding errors with the way floating point numbers are
    stored
    """
    # attempt to defeat some rounding errors prevalent in python
    if precision:
        quantize = decimal.Decimal(str(1 / math.pow(10, int(precision))))
    current = decimal.Decimal(str(start))
    if precision:
        current = current.quantize(quantize)

    dstop = decimal.Decimal(str(stop))
    dstep = decimal.Decimal(str(step))
    while current < dstop:
        # inefficient?
        yield float(str(current))
        current = current + dstep
        if precision:
            current = current.quantize(quantize)
