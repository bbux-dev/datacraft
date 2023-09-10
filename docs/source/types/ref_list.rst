ref_list
--------

Pointer to Field Specs to be injected into list in order of name. This allows externally defined
fields to be injected into specific places in a list of values.

Prototype:

.. code-block:: python

    {
      "<field name>": {
        "type": "ref_list":
        "refs": ["<ref_name>", "<ref_name>", ...,"<ref_name>"]
        or
        "data": ["<ref_name>", "<ref_name>", ...,"<ref_name>"]
        "config": {
          "key": Any
        }
      }
    }

Examples:

.. code-block:: json

    { "pointer": { "type": "ref_list", "data": "refs": ["one", "two"] }, "refs": { "refs": ["one", "two"] } }

    { "pointer": { "type": "ref_list", "refs": ["one", "two"] }, "refs": { "one": 1, "two": 2 } }

    { "pointer:ref_list": { "refs": ["one", "two"] }, "refs": { "one": 1, "two": 2 } }

    { "pointer:ref_list": { "data": ["one", "two"] }, "refs": { "one": 1, "two": 2 } }

    { "pointer:ref_list": ["one", "two"], "refs": { "one": 1, "two": 2 } }