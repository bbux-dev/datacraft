sample
------

A sample spec is used to select multiple values from a list to use as the value for a field.

Prototype:

.. code-block:: text

    {
      "<field name>": {
        "type": "sample",
        OR
        "type": "sample", $ <- legacy name
        "config": {
          "mean": N,
          "stddev": N,
          "min": N,
          "max": N,
          or
          "count": N,
          "join_with": "<optional delimiter to join with>"
        },
        "data": ["data", "to", "select", "from"],
        OR
        "ref": "REF_WITH_DATA_AS_LIST"
      }
    }

Examples:

.. code-block:: json

    {
      "ingredients": {
        "type": "sample",
        "data": ["onions", "mushrooms", "garlic", "bell peppers", "spinach", "potatoes", "carrots"],
        "config": {
          "mean": 3,
          "stddev": 1,
          "min": 2,
          "max": 4,
          "join_with": ", "
        }
      }
    }

.. code-block:: json

    {
      "ingredients": {
        "type": "sample",
        "data": ["onions", "mushrooms", "garlic", "bell peppers", "spinach", "potatoes", "carrots"],
        "config": {
          "mean": 3,
          "stddev": 1,
          "min": 2,
          "max": 4,
          "join_with": "\", \"",
          "quote": "\""
        }
      }
    }
