"""
A weighted ref spec is used to select the values from a set of refs in a weighted fashion.

Prototype:

.. code-block:: python

    {
      "<field name>": {
        "type": "weightedref",
        "data": {"valid_ref_1": 0.N, "valid_ref_2": 0.N, ...}
        "config": {
          "key": Any
        }
      }
    }

Examples:

.. code-block:: json

    {
      "http_code": {
        "type": "weightedref",
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
