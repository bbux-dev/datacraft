"""
For nested fields

Prototype:

.. code-block:: python

    {
      "<field name>": {
        "type": "nested",
        "config": {
          "count": "Values Spec for Counts, default is 1"
        },
        "fields": {
          "<sub field one>": { spec definition here },
          "<sub field two>": { spec definition here },
          ...
        }
      }
    }

Examples:

.. code-block:: json

    {
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

"""
from typing import Dict, Any

import datagen
import datagen.model


class NestedSupplier(datagen.model.ValueSupplierInterface):
    """
    Implementation for Nested Value Supplier
    """

    def __init__(self,
                 field_supplier_map: Dict[str, datagen.model.ValueSupplierInterface],
                 count_supplier: datagen.model.ValueSupplierInterface,
                 as_list: bool):
        """
        Args:
            field_supplier_map: mapping of nested field name to value supplier for it
            count_supplier: number of nested objects to create
            as_list: for counts of one, if the result should be a list instead of an object
        """
        self.field_supplier_map = field_supplier_map
        self.count_supplier = count_supplier
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
        return {key: supplier.next(iteration) for key, supplier in self.field_supplier_map.items()}


@datagen.registry.types('nested')
def _configure_nested_supplier(spec, loader):
    """ configure the supplier for nested types """
    fields = spec['fields']
    keys = [key for key in fields.keys() if key not in loader.RESERVED]
    config = datagen.utils.load_config(spec, loader)
    count_supplier = datagen.suppliers.count_supplier_from_data(config.get('count', 1))
    as_list = datagen.utils.is_affirmative('as_list', config)

    field_supplier_map = {}
    # each non reserved key should have a valid spec as a value
    for key in keys:
        nested_spec = fields[key]
        if 'type' in nested_spec and nested_spec.get('type') == 'nested':
            supplier = _configure_nested_supplier(nested_spec, loader)
        else:
            supplier = loader.get_from_spec(nested_spec)
        field_supplier_map[key] = supplier
    return NestedSupplier(field_supplier_map, count_supplier, as_list)
