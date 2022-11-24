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
          "key": "value"
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

    $ datacraft -s spec.json -i 3 -r 1 --format json -x --log-level off
    {"short_hand_field_weighted_with_null": "200"}
    {"short_hand_field_weighted_with_null": null}
    {"short_hand_field_weighted_with_null": "200"}

Special Output Values
^^^^^^^^^^^^^^^^^^^^^

There are certain valid JSON output values that are trickier to produce with a values spec. There are also times when
your values are interpreted as strings but you need them to be output as one of these special values. The way
we do this is by using a special token of the form ``_TYPE_``.  Below is the current mappings of special token to
output value:

.. code-block:: json

   {
       "_NONE_": null,
       "_NULL_": null,
       "_NIL_": null,
       "_TRUE_": true,
       "_FALSE_": false
   }

This is particularly useful when using a weighted values form of the values spec:

.. code-block:: json

    {
        "converted": {
            "type": "values",
            "data": {
                "_TRUE_": 0.05,
                "_FALSE_": 0.95
            }
        }
    }

.. code-block:: text

    $ datacraft -s /tmp/spec.json -i 3 -r 1 --format json -x --log-level off
    {"converted": false}
    {"converted": false}
    {"converted": false}

The special token values can be mixed and matched as well:

.. code-block:: json

    {
        "mixed": {
            "type": "values",
            "data": {
                "_NONE_": 0.11,
                "_NULL_": 0.11,
                "_NIL_": 0.11,
                "_TRUE_": 0.33,
                "_FALSE_": 0.33
            }
        }
    }

.. code-block:: text

    $ datacraft -s /tmp/spec.json -i 3 -r 1 --format json -x --log-level off
    {"mixed": false}
    {"mixed": true}
    {"mixed": null}
