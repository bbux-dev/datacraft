values
------
There are three types of values specs: Constants, List, and Weighted. Values specs have a shorthand notation where
the value of the data element replaces the full spec. See examples below.

Prototype:

.. code-block:: python

    {
      "<field_name>": {
        "type": "values",
        "data": Union[str, bool, int, float, list, dict],
        "config": {
          "key": Any
        }
      }
    }

Examples:

.. code-block:: json

    {"field_constant": {"type": "values", "data": 42}}

.. code-block:: json

    {"field_list": {"type": "values", "data": [1, 2, 3, 5, 8, 13]}}

.. code-block:: json

    {"field_weighted": {"type": "values", "data": {"200": 0.6, "404": 0.1, "303": 0.3}}}

.. code-block:: json

    {"shorthand_field_constant": 42}

.. code-block:: json

    {"shorthand_field_list": [1, 2, 3, 5, 8, 13]}

.. code-block:: json

    {"shorthand_field_weighted": {"200": 0.6, "404": 0.1, "303": 0.3}}