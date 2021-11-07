"""
Constant, list, or weighted dictionary

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
"""

import datagen

_VALUES_KEY = 'values'


@datagen.registry.schemas(_VALUES_KEY)
def _get_schema():
    """ returns the values schema """
    return datagen.schemas.load(_VALUES_KEY)
