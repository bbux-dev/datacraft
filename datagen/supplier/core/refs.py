"""
Pointer to a field spec defined in references section

Prototype:

.. code-block:: python

    {
      "<field name>": {
        "type": "ref":
        "ref": "<ref_name>",
        or
        "data": <ref_name>,
        "config": {
          "key": Any
        }
      }
    }

Examples:

.. code-block:: json

    { "pointer": { "type": "ref", "data": "ref_name" } }, "refs": { "ref_name": 42 } }

    { "pointer": { "type": "ref", "ref": "ref_name" } }, "refs": { "ref_name": 42 } }

    { "pointer:ref": { "ref": "ref_name" } }, "refs": { "ref_name": 42 } }

    { "pointer:ref": { "data": "ref_name" } }, "refs": { "ref_name": 42 } }

"""
import json
import datagen


@datagen.registry.types('ref')
def _configure_ref_supplier(field_spec: dict, loader: datagen.Loader):
    """ configures supplier for ref type """
    key = None
    if 'data' in field_spec:
        key = field_spec.get('data')
    if 'ref' in field_spec:
        key = field_spec.get('ref')
    if key is None:
        raise datagen.SpecException('No key found for spec: ' + json.dumps(field_spec))
    return loader.get(key)
