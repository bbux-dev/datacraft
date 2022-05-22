refs
----

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

    { "pointer:ref": "ref_name", "refs": { "ref_name": 42 } }