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

Example:

In this example we want a location field as a list of [latitude, longitude, altitude]

.. code-block:: json

    {
      "location": {
        "type": "ref_list",
        "refs": ["lat", "long", "altitude"]
      },
      "refs": {
        "lat": {
          "type": "geo.lat"
        },
        "long": {
          "type": "geo.long"
        },
        "altitude": {
          "type": "rand_int_range",
          "data": [5000, 10000]
        }
      }
    }

.. code-block:: bash

    $ datacraft -s spec.json -i 1 --format json-pretty -x -l off
    [
        {
            "location": [
                -36.7587,
                -40.5453,
                6233
            ]
        }
    ]