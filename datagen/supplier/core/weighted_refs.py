"""
This module handles the weightedref type.

A weighted ref spec is used to select the values from a set of refs in a weighted fashion.
"""
from typing import Dict

import datagen


class WeightedRefsSupplier(datagen.ValueSupplierInterface):
    """
    Value supplier that uses a weighted scheme to supply values from different reference value suppliers
    """

    def __init__(self,
                 key_supplier: datagen.ValueSupplierInterface,
                 values_map: Dict[str, datagen.ValueSupplierInterface]):
        """
        Args:
            key_supplier: supplier for ref keys
            values_map: mapping of ref name to supplier for ref
        """
        self.key_supplier = key_supplier
        self.values_map = values_map

    def next(self, iteration):
        key = self.key_supplier.next(iteration)
        supplier = self.values_map.get(key)
        if supplier is None:
            raise datagen.SpecException("Unknown Key '%s' for Weighted Reference" % key)
        return supplier.next(iteration)


@datagen.registry.types('weightedref')
def _configure_supplier(parent_field_spec, loader):
    """ configures supplier for weighted ref specs """
    config = datagen.utils.load_config(parent_field_spec, loader)
    data = parent_field_spec['data']
    key_supplier = datagen.suppliers.values(data)
    values_map = {}
    for key in data.keys():
        supplier = loader.get(key)
        values_map[key] = supplier
    supplier = WeightedRefsSupplier(key_supplier, values_map)
    if 'count' in config:
        return datagen.suppliers.array_supplier(supplier, config)
    return supplier
