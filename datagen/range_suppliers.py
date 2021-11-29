"""
Module for range related types: range and rand_range
"""
import decimal
import json
import math

from . import types, schemas, suppliers, utils
from .exceptions import SpecException

RANGE_KEY = 'range'
RAND_RANGE_KEY = 'rand_range'
RAND_INT_RANGE_KEY = 'rand_int_range'


@types.registry.schemas(RANGE_KEY)
def _get_range_schema():
    """ schema for range type """
    return schemas.load(RANGE_KEY)


@types.registry.schemas(RAND_RANGE_KEY)
def _get_rand_range_schema():
    """ schema for rand range type """
    # This shares a schema with range
    return schemas.load(RANGE_KEY)


@types.registry.schemas(RAND_INT_RANGE_KEY)
def _get_rand_int_range_schema():
    """ schema for rand int range type """
    # This shares a schema with range
    return schemas.load(RANGE_KEY)


@types.registry.types(RANGE_KEY)
def _configure_range_supplier(field_spec, _):
    """ configures the range value supplier """
    if 'data' not in field_spec:
        raise SpecException('No data element defined for: %s' % json.dumps(field_spec))

    data = field_spec.get('data')
    if not isinstance(data, list) or len(data) < 2:
        raise SpecException(
            'data element for ranges type must be list with at least two elements: %s' % json.dumps(field_spec))
    # we have the nested case
    if isinstance(data[0], list):
        suppliers_list = [_configure_supplier_for_data(field_spec, subdata) for subdata in data]
        return suppliers.from_list_of_suppliers(suppliers_list, True)
    return _configure_supplier_for_data(field_spec, data)


def _configure_supplier_for_data(field_spec, data):
    """ configures the supplier based on the range data supplied """
    start = data[0]
    # default for built in range function is exclusive end, we want to default to inclusive as this is the
    # more intuitive behavior
    end = data[1] + 1
    if not end > start:
        raise SpecException('end element must be larger than start: %s' % json.dumps(field_spec))
    if len(data) == 2:
        step = 1
    else:
        step = data[2]
    if _any_is_float(data):
        config = field_spec.get('config', {})
        precision = config.get('precision', None)
        if precision and not str(precision).isnumeric():
            raise SpecException(f'precision must be valid integer {json.dumps(field_spec)}')
        range_values = list(_float_range(float(start), float(end), float(step), precision))
    else:
        range_values = list(range(start, end, step))
    return suppliers.values(range_values)


@types.registry.types(RAND_INT_RANGE_KEY)
def _configure_rand_int_range_supplier(field_spec, loader):
    """ configures the random int range value supplier """
    config = utils.load_config(field_spec, loader)
    config['cast'] = 'int'
    field_spec['config'] = config
    return _configure_rand_range_supplier(field_spec, loader)


@types.registry.types(RAND_RANGE_KEY)
def _configure_rand_range_supplier(field_spec, loader):
    """ configures the random range value supplier """
    if 'data' not in field_spec:
        raise SpecException('No data element defined for: %s' % json.dumps(field_spec))
    data = field_spec.get('data')
    config = utils.load_config(field_spec, loader)
    if not isinstance(data, list) or len(data) == 0:
        raise SpecException(
            'rand_range specs require data as array with at least one element: %s' % json.dumps(field_spec))
    start = 0
    end = 0
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
    return suppliers.random_range(start, end, precision)


def _any_is_float(data):
    """ are any of the items floats """
    for item in data:
        if isinstance(item, float):
            return True
    return False


def _float_range(start: float,
                 stop: float,
                 step: float,
                 precision=None):
    """
    Fancy foot work to support floating point ranges due to rounding errors with the way floating point numbers are
    stored
    """
    # attempt to defeat some rounding errors prevalent in python
    current = decimal.Decimal(str(start))
    if precision:
        quantize = decimal.Decimal(str(1 / math.pow(10, int(precision))))
        current = current.quantize(quantize)

    dstop = decimal.Decimal(str(stop))
    dstep = decimal.Decimal(str(step))
    while current < dstop:
        # inefficient?
        yield float(str(current))
        current = current + dstep
        if precision:
            current = current.quantize(quantize)
