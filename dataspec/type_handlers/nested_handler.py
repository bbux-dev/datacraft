"""
Module for handling nested types
"""
from dataspec import registry, ValueSupplierInterface


class NestedSupplier(ValueSupplierInterface):
    """
    Implementation for Nested Value Supplier
    """
    def __init__(self, field_supplier_map):
        self.field_supplier_map = field_supplier_map

    def next(self, iteration):
        return {key: supplier.next(iteration) for key, supplier in self.field_supplier_map.items()}


@registry.types('nested')
def configure_nested_supplier(spec, loader):
    """ configure the supplier for nested types """
    keys = [key for key in spec.keys() if key not in loader.RESERVED]
    field_supplier_map = {}
    # each non reserved key should have a valid spec as a value
    for key in keys:
        nested_spec = spec[key]
        if nested_spec.get('type') == 'nested':
            supplier = configure_nested_supplier(nested_spec, loader)
        else:
            supplier = loader.get_from_spec(nested_spec)
        field_supplier_map[key] = supplier
    return NestedSupplier(field_supplier_map)
