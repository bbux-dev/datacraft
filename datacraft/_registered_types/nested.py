"""module for nested type datacraft registry functions"""
import logging
from typing import Dict, Any

import datacraft
from datacraft import ValueSupplierInterface, KeyProviderInterface, SupplierException
from datacraft.supplier import key_suppliers
from . import common
from . import schemas

_log = logging.getLogger(__name__)
_NESTED_KEY = 'nested'


@datacraft.registry.schemas(_NESTED_KEY)
def _get_nested_schema():
    """ schema for nested type """
    return schemas.load(_NESTED_KEY)


@datacraft.registry.types(_NESTED_KEY)
def _configure_nested_supplier(spec, loader):
    """ configure the supplier for nested types """
    fields = spec['fields']
    keys = list(fields.keys())
    config = datacraft.utils.load_config(spec, loader)
    count_supplier = datacraft.suppliers.count_supplier(**config)
    if 'field_groups' in spec:
        key_supplier = key_suppliers.from_spec(spec)
    else:
        key_supplier = key_suppliers.from_spec(fields)

    as_list = datacraft.utils.is_affirmative('as_list', config)

    field_supplier_map = {}
    # each non reserved key should have a valid spec as a value
    for key in keys:
        nested_spec = fields[key]
        if 'type' in nested_spec and nested_spec.get('type') == _NESTED_KEY:
            supplier = _configure_nested_supplier(nested_spec, loader)
        else:
            supplier = loader.get_from_spec(nested_spec)
        field_supplier_map[key] = supplier
    return nested_supplier(field_supplier_map, count_supplier, key_supplier, as_list)


@datacraft.registry.usage(_NESTED_KEY)
def _example_nested_usage():
    example = {
        "id": {
            "type": "uuid"
        },
        "user": {
            "type": "nested",
            "fields": {
                "user_id": {
                    "type": "uuid"
                },
                "geo": {
                    "type": "nested",
                    "fields": {
                        "place_id:cc-digits?mean=5": {},
                        "coordinates:geo.pair?as_list=true": {}
                    }
                }
            }
        }
    }
    return common.standard_example_usage(example, 1, pretty=True)


def nested_supplier(field_supplier_map: Dict[str, ValueSupplierInterface],
                    count_supplier: ValueSupplierInterface,
                    key_supplier: KeyProviderInterface,
                    as_list: bool) -> ValueSupplierInterface:
    """
    Args:
        field_supplier_map: mapping of nested field name to value supplier for it
        count_supplier: number of nested objects to create
        key_supplier: to supply nest fields names
        as_list: for counts of one, if the result should be a list instead of an object
    """
    return _NestedSupplier(field_supplier_map, count_supplier, key_supplier, as_list)


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
        """ get set of values for this iteration """
        _, keys = self.key_supplier.get()
        subset = {key: self.field_supplier_map.get(key) for key in keys}
        if any(val is None for val in subset.values()):
            raise SupplierException(f'One or more keys provided in nested spec are not valid: {keys}, valid keys: '
                                    f'{list(self.field_supplier_map.keys())}')
        return {key: supplier.next(iteration) for key, supplier in subset.items()}  # type: ignore
