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

.. code-block:: python

    {"field_list": {"type": "values", "data": [1, 2, 3, 5, 8, 13, None]}}

.. code-block:: json

    {"field_weighted": {"type": "values", "data": {"200": 0.6, "404": 0.1, "303": 0.3}}}

.. code-block:: json

    {"field_weighted_with_null": {"type": "values", "data": {"200": 0.5, "404": 0.1, "303": 0.3, "_NULL_": 0.1}}}

.. code-block:: json

    {"shorthand_field_constant": 42}

.. code-block:: json

    {"shorthand_field_list": [1, 2, 3, 5, 8, 13]}

.. code-block:: json

    {"shorthand_field_weighted": {"200": 0.6, "404": 0.1, "303": 0.3}}

.. code-block:: json

    {
        "short_hand_field_weighted_with_null": {
            "type": "values",
            "data": {"200": 0.5, "404": 0.1, "303": 0.3, "_NONE_": 0.1}
        }
    }

.. code-block:: text

    $ datacraft -s spec.json -i 3 --format json -x --log-level off
    {"short_hand_field_weighted_with_null": "200"}
    {"short_hand_field_weighted_with_null": null}
    {"short_hand_field_weighted_with_null": "200"}