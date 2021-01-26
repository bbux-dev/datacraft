import json
from .exceptions import SpecException
from .supplier.list_values import ListValueSupplier
from .supplier.combine import CombineValuesSupplier
from .supplier.weighted_values import WeightedValueSupplier
from .supplier.weighted_refs import WeightedRefsSupplier
from .supplier.select_list_subset import SelectListSupplier


def values(spec):
    """
    Based on data, return the appropriate values supplier
    """
    # shortcut notations no type, or data, the spec is the data
    if 'data' not in spec:
        data = spec
    else:
        data = spec['data']

    if isinstance(spec, dict) and 'config' in spec:
        config = spec['config']
        sample_mode = config.get('sample', 'false')
        do_sampling = sample_mode.lower() in ['yes', 'true', 'on']
    else:
        do_sampling = False

    if isinstance(data, list):
        return value_list(data, do_sampling)
    elif isinstance(data, dict):
        if do_sampling:
            raise SpecException('Cannot do sampling on weighted values: ' + json.dumps(spec))
        return weighted_values(data)
    else:
        return single_value(data)


class _SingleValue:
    def __init__(self, data):
        self.data = data

    def next(self, _):
        return self.data


def single_value(data):
    return _SingleValue(data)


def value_list(data, do_sampling=False):
    """
    creates a value list supplier
    :param spec: for the supplier
    :return: the supplier
    """
    return ListValueSupplier(data, do_sampling)


def weighted_values(data):
    """
    creates a weighted value supplier
    :param data: for the supplier
    :return: the supplier
    """
    return WeightedValueSupplier(data)


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


def select_list_subset(data, config):
    """
    select list subset supplier
    :param data: list to select subset from
    :param config: with minimal of mean specified
    :return: the supplier
    """
    return SelectListSupplier(data, config)


def isdecorated(data_spec):
    """
    is this spec a decorated one
    :param data_spec: to check
    :return: true or false
    """
    if 'config' not in data_spec:
        return False
    config = data_spec.get('config')
    return 'prefix' in config or 'suffix' in config or 'quote' in config


class DecoratedSupplier:
    def __init__(self, config, supplier):
        self.prefix = config.get('prefix', '')
        self.suffix = config.get('suffix', '')
        self.quote = config.get('quote', '')
        self.wrapped = supplier

    def next(self, iteration):
        value = self.wrapped.next(iteration)
        # todo: cache mapping for efficiency?
        return self.quote + self.prefix + str(value) + self.suffix + self.quote


def decorated(data_spec, supplier):
    """
    Creates a decorated supplier around the provided on
    :param data_spec: the spec
    :param supplier: the supplier to decorate
    :return: the decorated supplier
    """
    return DecoratedSupplier(data_spec.get('config'), supplier)
