"""
Nested types are used to create fields that contain subfields. Nested types can
also contain nested fields to allow multiple levels of nesting. Use the ``nested``
type to generate a field that contains subfields. The subfields are defined in
the ``fields`` element of the nested spec. The ``fields`` element will be treated
like a top level DataSpec and has access to the ``refs`` and other elements of the
root.

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
        },
        "field_groups": <field groups format>
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

The same spec in a slightly more compact format

.. code-block:: json

    {
      "id:uuid": {},
      "user:nested": {
        "fields": {
          "user_id:uuid": {},
          "geo:nested": {
            "fields": {
              "place_id:cc-digits?mean=5": {},
              "coordinates:geo.pair?as_list=true": {}
            }
          }
        }
      }
    }

Generates the following structure

.. code-block:: console

    datagen -s tweet-geo.json --log-level off -x -i 1 --format json-pretty
    {
        "id": "68092478-2234-41aa-bcc6-e679950770d7",
        "user": {
            "user_id": "93b3c62e-76ad-4272-b3c1-b434be2c8c30",
            "geo": {
                "place_id": "5104987632",
                "coordinates": [
                    -93.0759,
                    68.2469
                ]
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
                 key_supplier: datagen.model.KeyProviderInterface,
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
            raise datagen.SpecException(f'One or more keys provided in nested spec are not valid: {keys}, valid keys: '
                                        f'{list(self.field_supplier_map.keys())}')
        return {key: supplier.next(iteration) for key, supplier in subset.items()}  # type: ignore


@datagen.registry.types('nested')
def _configure_nested_supplier(spec, loader):
    """ configure the supplier for nested types """
    fields = spec['fields']
    keys = [key for key in fields.keys() if key not in loader.RESERVED]
    config = datagen.utils.load_config(spec, loader)
    count_supplier = datagen.suppliers.count_supplier_from_data(config.get('count', 1))
    if 'field_groups' in spec:
        key_supplier = datagen.key_providers.from_spec(spec)
    else:
        key_supplier = datagen.key_providers.from_spec(fields)

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
    return NestedSupplier(field_supplier_map, count_supplier, key_supplier, as_list)
