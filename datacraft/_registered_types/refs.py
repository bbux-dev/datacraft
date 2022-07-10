"""module for refs type datacraft registry functions"""
import json
import logging
from typing import Dict

import datacraft
from datacraft import ValueSupplierInterface
from . import common
from . import schemas

_log = logging.getLogger(__name__)
_REF_KEY = 'ref'
_WEIGHTED_REF_KEY = 'weighted_ref'


@datacraft.registry.schemas(_REF_KEY)
def _get_ref_schema():
    """ schema for ref type """
    return schemas.load(_REF_KEY)


@datacraft.registry.types(_REF_KEY)
def _configure_ref_supplier(field_spec: dict, loader: datacraft.Loader):
    """ configures supplier for ref type """
    key = None
    if 'data' in field_spec:
        key = field_spec.get('data')
    if 'ref' in field_spec:
        key = field_spec.get('ref')
    if key is None:
        raise datacraft.SpecException('No key found for spec: ' + json.dumps(field_spec))
    return loader.get(key)


@datacraft.registry.schemas(_WEIGHTED_REF_KEY)
def _weighted_ref_schema():
    """ schema for weighted_ref type """
    return schemas.load(_WEIGHTED_REF_KEY)


@datacraft.registry.types(_WEIGHTED_REF_KEY)
def _configure_weighted_ref_supplier(parent_field_spec, loader):
    """ configures supplier for weighted ref specs """
    config = datacraft.utils.load_config(parent_field_spec, loader)
    data = parent_field_spec['data']
    key_supplier = datacraft.suppliers.values(data)
    values_map = {}
    for key in data.keys():
        supplier = loader.get(key)
        values_map[key] = supplier
    supplier = weighted_ref_supplier(key_supplier, values_map)
    if 'count' in config:
        return datacraft.suppliers.array_supplier(supplier, **config)
    return supplier


@datacraft.registry.usage(_REF_KEY)
def _example_ref_usage():
    example = {"pointer": {"type": _REF_KEY, "data": "ref_name"}, "refs": {"ref_name": 42}}
    return common.standard_example_usage(example, 3)


@datacraft.registry.usage(_WEIGHTED_REF_KEY)
def _example_weighted_ref_usage():
    example = {
        "http_code": {
            "type": _WEIGHTED_REF_KEY,
            "data": {"GOOD_CODES": 0.7, "BAD_CODES": 0.3}
        },
        "refs": {
            "GOOD_CODES": {
                "200": 0.5,
                "202": 0.3,
                "203": 0.1,
                "300": 0.1
            },
            "BAD_CODES": {
                "400": 0.5,
                "403": 0.3,
                "404": 0.1,
                "500": 0.1
            }
        }
    }
    return common.standard_example_usage(example, 3)


def weighted_ref_supplier(key_supplier: ValueSupplierInterface,
                          values_map: Dict[str, ValueSupplierInterface]) -> ValueSupplierInterface:
    """
    Args:
        key_supplier: supplier for ref keys
        values_map: mapping of ref name to supplier for ref
    """
    return _WeightedRefsSupplier(key_supplier, values_map)


class _WeightedRefsSupplier(ValueSupplierInterface):
    """
    Value supplier that uses a weighted scheme to supply values from different reference value suppliers
    """

    def __init__(self,
                 key_supplier: ValueSupplierInterface,
                 values_map: Dict[str, ValueSupplierInterface]):
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
            raise datacraft.SupplierException(f"Unknown Key '{key}' for Weighted Reference")
        return supplier.next(iteration)
