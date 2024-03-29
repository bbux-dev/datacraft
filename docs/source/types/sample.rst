sample
------

A sample spec is used to select multiple values from a list to use as the value for a field.

Prototype:

.. code-block:: text

    {
      "<field name>": {
        "type": "sample",
        OR
        "type": "sample",
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
        "ref": "<ref or field with data  as list>"
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

.. code-block:: text

    $ datacraft -s sample.json  -i 3 -t 'Ingredients: {{ ingredients | safe }}' -l off
    Ingredients: "garlic", "onions"
    Ingredients: "mushrooms", "potatoes", "garlic", "bell peppers"
    Ingredients: "potatoes", "mushrooms"
