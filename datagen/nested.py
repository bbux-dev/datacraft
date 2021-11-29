"""
Module for nested types
"""
from typing import Dict, Any

from . import types, schemas
from . import utils, suppliers
from .exceptions import SpecException
from .supplier import key_suppliers
from .supplier.model import ValueSupplierInterface, KeyProviderInterface


class _NestedSupplier(ValueSupplierInterface):
    """
    Implementation for Nested Value Supplier
    """

    def __init__(self,
                 field_supplier_map: Dict[str, ValueSupplierInterface],
                 count_supplier: ValueSupplierInterface,
                 key_supplier: KeyProviderInterface,
                 as_list: bool):
        """
        Args:
            field_supplier_map: mapping of nested field name to value supplier for it
            count_supplier: number of nested objects to create
            key_supplier: to supply nest fields names
            as_list: for counts of one, if the result should be a list instead of an object
        """
        self.field_supplier_map = field_supplier_map
        self.count_supplier = count_supplier
        self.key_supplier = key_supplier
        self.as_list = as_list

    def next(self, iteration: int):
        count = int(self.count_supplier.next(iteration))
        if count == 0:
            if self.as_list:
                return []
            return None
        if count > 1:
            vals = [self._single_pass(iteration + i) for i in range(count)]
            return vals
        # this is dict
        vals = self._single_pass(iteration)  # type: ignore
        if self.as_list:
            return [vals]
        return vals

    def _single_pass(self, iteration: int) -> Dict[str, Any]:
        _, keys = self.key_supplier.get()
        subset = {key: self.field_supplier_map.get(key) for key in keys}
        if any(val is None for val in subset.values()):
            raise SpecException(f'One or more keys provided in nested spec are not valid: {keys}, valid keys: '
                                        f'{list(self.field_supplier_map.keys())}')
        return {key: supplier.next(iteration) for key, supplier in subset.items()}  # type: ignore


@types.registry.schemas('nested')
def _get_nested_schema():
    return schemas.load('nested')


@types.registry.types('nested')
def _configure_nested_supplier(spec, loader):
    """ configure the supplier for nested types """
    fields = spec['fields']
    keys = [key for key in fields.keys() if key not in loader.RESERVED]
    config = utils.load_config(spec, loader)
    count_supplier = suppliers.count_supplier_from_data(config.get('count', 1))
    if 'field_groups' in spec:
        key_supplier = key_suppliers.from_spec(spec)
    else:
        key_supplier = key_suppliers.from_spec(fields)

    as_list = utils.is_affirmative('as_list', config)

    field_supplier_map = {}
    # each non reserved key should have a valid spec as a value
    for key in keys:
        nested_spec = fields[key]
        if 'type' in nested_spec and nested_spec.get('type') == 'nested':
            supplier = _configure_nested_supplier(nested_spec, loader)
        else:
            supplier = loader.get_from_spec(nested_spec)
        field_supplier_map[key] = supplier
    return _NestedSupplier(field_supplier_map, count_supplier, key_supplier, as_list)
