import json
import logging
from typing import Dict

from datacraft import ValueSupplierInterface

import datacraft
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
            raise datacraft.SupplierException("Unknown Key '%s' for Weighted Reference" % key)
        return supplier.next(iteration)