"""module for range_suppliers type datacraft registry functions"""
import json
import logging

import datacraft
from . import common
from . import schemas

_log = logging.getLogger(__name__)
_RANGE_KEY = 'range'
_RAND_RANGE_KEY = 'rand_range'
_RAND_INT_RANGE_KEY = 'rand_int_range'


@datacraft.registry.schemas(_RANGE_KEY)
def _get_range_schema():
    """ schema for range type """
    return schemas.load(_RANGE_KEY)


@datacraft.registry.schemas(_RAND_RANGE_KEY)
def _get_rand_range_schema():
    """ schema for rand range type """
    # This shares a schema with range
    return schemas.load(_RANGE_KEY)


@datacraft.registry.schemas(_RAND_INT_RANGE_KEY)
def _get_rand_int_range_schema():
    """ schema for rand int range type """
    # This shares a schema with range
    return schemas.load(_RANGE_KEY)


@datacraft.registry.types(_RANGE_KEY)
def _configure_range_supplier(field_spec, _):
    """ configures the range value supplier """
    if 'data' not in field_spec:
        raise datacraft.SpecException(f'No data element defined for: {json.dumps(field_spec)}')

    data = field_spec.get('data')
    if not isinstance(data, list) or len(data) < 2:
        raise datacraft.SpecException(
            f'data element for ranges type must be list with at least two elements:{json.dumps(field_spec)}')
    # we have the nested case
    if isinstance(data[0], list):
        suppliers_list = [_configure_range_supplier_for_data(field_spec, subdata) for subdata in data]
        return datacraft.suppliers.from_list_of_suppliers(suppliers_list, True)
    return _configure_range_supplier_for_data(field_spec, data)


@datacraft.registry.usage(_RANGE_KEY)
def _example_range_usage():
    example = {
        "zero_to_ten_step_half": {
            "type": _RANGE_KEY,
            "data": [0, 10, 0.5]
        }
    }
    return common.standard_example_usage(example, 3)


@datacraft.registry.usage(_RAND_RANGE_KEY)
def _example_rand_range_usage():
    example = {
        "four_digits_precision": {
            "type": _RAND_RANGE_KEY,
            "data": [0, 10, 4]
        }
    }
    return common.standard_example_usage(example, 3)


@datacraft.registry.usage(_RAND_INT_RANGE_KEY)
def _example_range_int_range_usage():
    example = {
        "rand_0_to_99": {
            "type": _RAND_INT_RANGE_KEY,
            "data": [0, 100]
        }
    }
    return common.standard_example_usage(example, 3)


def _configure_range_supplier_for_data(field_spec, data):
    """ configures the supplier based on the range data supplied """
    config = field_spec.get('config', {})
    precision = config.get('precision', None)
    if precision and not str(precision).isnumeric():
        raise datacraft.SpecException(f'precision must be valid integer {json.dumps(field_spec)}')

    start = data[0]
    # default for built in range function is exclusive end, we want to default to inclusive as this is the
    # more intuitive behavior
    end = data[1] + 1
    if not end > start:
        raise datacraft.SpecException(f'end element must be larger than start:{json.dumps(field_spec)}')
    if len(data) == 2:
        step = 1
    else:
        step = data[2]
    try:
        return datacraft.suppliers.range_supplier(start, end, step, precision=precision)
    except ValueError as err:
        raise datacraft.SpecException(str(err)) from err


@datacraft.registry.types(_RAND_INT_RANGE_KEY)
def _configure_rand_int_range_supplier(field_spec, loader):
    """ configures the random int range value supplier """
    config = datacraft.utils.load_config(field_spec, loader)
    config['cast'] = 'int'
    field_spec['config'] = config
    return _configure_rand_range_supplier(field_spec, loader)


@datacraft.registry.types(_RAND_RANGE_KEY)
def _configure_rand_range_supplier(field_spec, loader):
    """ configures the random range value supplier """
    if 'data' not in field_spec:
        raise datacraft.SpecException(f'No data element defined for: {json.dumps(field_spec)}')
    data = field_spec.get('data')
    config = datacraft.utils.load_config(field_spec, loader)
    if not isinstance(data, list) or len(data) == 0:
        raise datacraft.SpecException(
            f'rand_range specs require data as array with at least one element: {json.dumps(field_spec)}')
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
    return datacraft.suppliers.random_range(start, end, precision)
