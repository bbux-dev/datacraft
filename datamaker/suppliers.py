from .supplier.list_values import ListValueSupplier
from .supplier.combine import CombineValuesSupplier
from .supplier.weighted_values import WeightedValueSupplier
from .supplier.weighted_refs import WeightedRefsSupplier


def values(spec):
    """
    Based on data, return the appropriate supplier
    """
    data = spec['data']
    if isinstance(data, list):
        return value_list(spec)
    elif isinstance(data, dict):
        return weighted_values(spec)
    else:
        return single_value(spec)


class _SingleValue(object):
    def __init__(self, spec):
        self.data = spec.get('data')
    def next(self, _):
        return self.data


def single_value(spec):
    return _SingleValue(spec)


def value_list(spec):
    """
    creates a value list supplier
    :param spec: for the supplier
    :return: the supplier
    """
    return ListValueSupplier(spec)


def weighted_values(spec):
    """
    creates a weighted value supplier
    :param spec: for the supplier
    :return: the supplier
    """
    return WeightedValueSupplier(spec)


def combine(suppliers, config=None):
    """
    combine supplier
    :param suppliers: to combine value for
    :param config: for the combiner
    :return: the supplier
    """
    return CombineValuesSupplier(suppliers, config)


def weighted_ref(key_supplier, values_map):
    """
    weighted refs supplier
    :param key_supplier: supplies weighted keys
    :param values_map: map of key to supplier for that key
    :return: the supplier
    """
    return WeightedRefsSupplier(key_supplier, values_map)