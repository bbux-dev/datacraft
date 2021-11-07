"""
A combine Field Spec is used to concatenate or append two or more fields or reference to one another.
There are two combine types: ``combine`` and ``combine-list``.

combine
-------

Prototype:

.. code-block:: python

    {
      "<field name>": {
        "type": "combine",
        "fields": ["valid field name1", "valid field name2"],
        OR
        "refs": ["valid ref1", "valid ref2"],
        "config": {
          "join_with": "<optional string to use to join fields or refs, default is none>"
        }
      }
    }

Examples:

.. code-block:: json

    {
      "combine": {
        "type": "combine",
        "refs": ["first", "last"],
        "config": {
          "join_with": " "
        }
      },
      "refs": {
        "first": {
          "type": "values",
          "data": ["zebra", "hedgehog", "llama", "flamingo"]
        },
        "last": {
          "type": "values",
          "data": ["jones", "smith", "williams"]
        }
      }
    }

combine-list
------------

Prototype:

.. code-block:: python

    {
      "<field name>": {
        "type": "combine-list",
        "refs": [
          ["valid ref1", "valid ref2"],
          ["valid ref1", "valid ref2", "valid_ref3", ...], ...
          ["another_ref", "one_more_ref"]
        ],
        "config": {
          "join_with": "<optional string to use to join fields or refs, default is none>"
        }
      }
    }

Examples:

.. code-block:: json

    {
      "full_name": {
        "type": "combine-list",
        "refs": [
          ["first", "last"],
          ["first", "middle", "last"],
          ["first", "middle_initial", "last"]
        ],
        "config": {
          "join_with": " "
        }
      },
      "refs": {
        "first": {
          "type": "values",
          "data": ["zebra", "hedgehog", "llama", "flamingo"]
        },
        "last": {
          "type": "values",
          "data": ["jones", "smith", "williams"]
        },
        "middle": {
          "type": "values",
          "data": ["cloud", "sage", "river"]
        },
        "middle_initial": {
          "type": "values",
          "data": {"a": 0.3, "m": 0.3, "j": 0.1, "l": 0.1, "e": 0.1, "w": 0.1}
        }
      }
    }

"""
from typing import List
import json

import datagen

COMBINE_KEY = 'combine'
COMBINE_LIST_KEY = 'combine-list'


class CombineValuesSupplier(datagen.ValueSupplierInterface):
    """
    Class for combining the values from the output of two or more value suppliers
    """

    def __init__(self,
                 suppliers: List[datagen.ValueSupplierInterface],
                 config: dict):
        """
        Args:
            suppliers: list of suppliers to combine in order of combination
            config: with optional as_list and join_with params
        """
        self.suppliers = suppliers
        self.as_list = config.get('as_list', datagen.types.get_default('combine_as_list'))
        self.joiner = config.get('join_with', datagen.types.get_default('combine_join_with'))

    def next(self, iteration):
        values = [str(supplier.next(iteration)) for supplier in self.suppliers]
        if self.as_list:
            return values
        return self.joiner.join(values)


@datagen.registry.schemas(COMBINE_KEY)
def _get_combine_schema():
    """ get the schema for the combine type """
    return datagen.schemas.load(COMBINE_KEY)


@datagen.registry.schemas(COMBINE_LIST_KEY)
def _get_combine_list_schema():
    """ get the schema for the combine_list type """
    return datagen.schemas.load(COMBINE_LIST_KEY)


@datagen.registry.types(COMBINE_KEY)
def _configure_combine_supplier(field_spec, loader):
    """ configures supplier for combine type """
    if 'refs' not in field_spec and 'fields' not in field_spec:
        raise datagen.SpecException('Must define one of fields or refs. %s' % json.dumps(field_spec))

    if 'refs' in field_spec:
        supplier = _load_from_refs(field_spec, loader)
    else:
        supplier = _load_from_fields(field_spec, loader)
    return supplier


@datagen.registry.types(COMBINE_LIST_KEY)
def _configure_combine_list_supplier(field_spec, loader):
    """ configures supplier for combine-list type """
    if 'refs' not in field_spec:
        raise datagen.SpecException('Must define refs for combine-list type. %s' % json.dumps(field_spec))

    refs_list = field_spec['refs']
    if len(refs_list) < 1 or not isinstance(refs_list[0], list):
        raise datagen.SpecException(
            'refs pointer must be list of lists: i.e [["ONE", "TWO"]]. %s' % json.dumps(field_spec))

    suppliers_list = []
    for ref in refs_list:
        spec = dict(field_spec)
        spec['refs'] = ref
        suppliers_list.append(_load_from_refs(spec, loader))
    return datagen.suppliers.from_list_of_suppliers(suppliers_list, True)


def _load_from_refs(combine_field_spec, loader):
    """ loads the combine type from a set of refs """
    keys = combine_field_spec.get('refs')
    return _load(combine_field_spec, keys, loader)


def _load_from_fields(combine_field_spec, loader):
    """ load the combine type from a set of field names """
    keys = combine_field_spec.get('fields')
    return _load(combine_field_spec, keys, loader)


def _load(combine_field_spec, keys, loader):
    """ create the combine supplier for the types from the given keys """
    to_combine = []
    for key in keys:
        supplier = loader.get(key)
        to_combine.append(supplier)
    config = combine_field_spec.get('config', {})
    return CombineValuesSupplier(to_combine, config)
