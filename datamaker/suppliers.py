from .supplier.list_values import ListValueSupplier
from .supplier.combine import CombineValuesSupplier


def value_list(spec):
    """
    creates a value list supplier
    :param spec: for the supplier
    :return: the supplier
    """
    return ListValueSupplier(spec)

def combine(suppliers, config=None):
    """
    combine supplier
    :param suppliers: to combine value for
    :param config: for the combiner
    :return: the supplier
    """
    return CombineValuesSupplier(suppliers, config)
