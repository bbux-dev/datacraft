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