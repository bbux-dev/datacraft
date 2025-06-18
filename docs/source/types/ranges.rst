range_suppliers
---------------

There are two main range types sequential and random.  A sequential range is
specified using the ``range`` type.  A random one uses the ``rand_range`` type.

range
^^^^^

Prototype:

.. code-block:: python

    {
      "<field name>": {
        "type": "range",
        "data": [<start>, <end>, <step> (optional)],
        or
        "data": [
          [<start>, <end>, <step> (optional)],
          [<start>, <end>, <step> (optional)],
          ...
          [<start>, <end>, <step> (optional)],
        ],
      }
    }

    start: (Union[int, float]) - start of range
    end: (Union[int, float]) - end of range
    step: (Union[int, float]) - step for range, default is 1

Examples:

.. code-block:: json

    {
      "zero_to_ten_step_half": {
        "type": "range",
        "data": [0, 10, 0.5]
      }
    }

.. code-block:: json

    {
      "range_shorthand1:range": {
        "data": [0, 10, 0.5]
      }
    }

.. code-block:: json

    {"range_shorthand2:range": [0, 10, 0.5]},

rand_range
^^^^^^^^^^

Generates a random floating point number in the given range. Use the `rand_int_range` type as a shortcut for casting
the numbers as integers.

Prototype:

.. code-block:: python

    {
      "<field name>": {
        "type": "rand_range",
        "data": [<upper>],
        or
        "data": [<lower>, <upper>],
        or
        "data": [<lower>, <upper>, <precision> (optional)]
      }
    }

    upper: (Union[int, float]) - upper limit of random range
    lower: (Union[int, float]) - lower limit of random range
    precision: (int) - Number of digits after decimal point

Examples:

.. code-block:: json

    {
      "zero_to_ten_three_decimals": {
        "type": "rand_range",
        "data": [0, 10, 3]
      }
    }

.. code-block:: json

    {
      "int_in_range": {
        "type": "rand_int_range",
        "data": [1, 100]
      }
    }

.. code-block:: json

    {
      "int_in_range": {
        "type": "rand_int_range",
        "data": [1, 100]
      }
    }

integer
^^^^^^^

The `integer` type is similar to `rand_int_range` and uses the same configuration. The only difference is that the
data element is not required. If no data element is specified, the range of numbers created will be between +- one
billion.

.. code-block:: json

    {
      "int_no_args": {
        "type": "integer"
      }
    }


.. code-block:: json

    {
      "int_with_args": {
        "type": "integer",
        "data": [
            [1, 5], [7, 11], [20, 122]
        ]
      }
    }

number
^^^^^^^

The `number` type is similar to `rand_range` and uses the same configuration. The only difference is that the
data element is not required. If no data element is specified, the range of numbers created will be between +- one
billion.

.. code-block:: json

    {
      "num_no_args": {
        "type": "number"
      }
    }


.. code-block:: json

    {
      "num_with_args": {
        "type": "number",
        "data": [
            [1.1, 5.5], [7.1, 11.33], [20.5, 122.66]
        ]
      }
    }

number.N
^^^^^^^^

The `number.N` type is a specialized version of the `number` type that automatically truncates decimal places to exactly N digits. 
This type is available for N = 1 through 7. It uses the same configuration as the `number` type but automatically applies 
a `roundN` cast to ensure consistent decimal precision.

Prototype:

.. code-block:: python

    {
      "<field name>": {
        "type": "number.<N>",
        "data": [<lower>, <upper>] (optional),
        or
        "data": [
          [<lower>, <upper>],
          [<lower>, <upper>],
          ...
          [<lower>, <upper>],
        ],
      }
    }

    N: (int) - Number of decimal places (1-7)
    lower: (Union[int, float]) - lower limit of random range
    upper: (Union[int, float]) - upper limit of random range

Examples:

.. code-block:: json

    {
      "two_decimal_places": {
        "type": "number.2",
        "data": [0, 10]
      }
    }

.. code-block:: json

    {
      "three_decimal_places": {
        "type": "number.3",
        "data": [1.1, 5.5]
      }
    }

.. code-block:: json

    {
      "one_decimal_place": {
        "type": "number.1",
        "data": [
            [0, 5], [10, 15]
        ]
      }
    }

.. code-block:: json

    {
      "four_decimal_places": {
        "type": "number.4"
      }
    }