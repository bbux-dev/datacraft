unicode_range
-------------

Generates strings from unicode ranges

Prototype:

.. code-block:: python

    {
      "<field>": {
        "type": "unicode_range":
        "data": [<start_code_point_in_hex>, <end_code_point_in_hex>],
        or
        "data": [
            [<start_code_point_in_hex>, <end_code_point_in_hex>],
            [<start_code_point_in_hex>, <end_code_point_in_hex>],
            ...
            [<start_code_point_in_hex>, <end_code_point_in_hex>],
        ],
        "config":{
          # String Size Based Config Parameters
          "min": <min number of characters in string>,
          "max": <max number of characters in string>,
          or
          "count": <exact number of characters in string>
          or
          "mean": <mean number of characters in string>
          "stddev": <standard deviation from mean for number of characters in string>
          "min": <optional min>
          "max": <optional max>
        }
      }
    }

Examples:

.. code-block:: json

    {
      "text": {
        "type": "unicode_range",
        "data": ["3040", "309f"],
        "config": {
          "mean": 5
        }
      }
    }
