weighted_refs
-------------
A weighted_ref spec is used to select the values from a set of refs in a weighted fashion.

Prototype:

.. code-block:: python

    {
      "<field name>": {
        "type": "weighted_ref",
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
        "type": "weighted_ref",
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
