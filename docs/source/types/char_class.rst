char_class
----------

A ``char_class`` type is used to create strings that are made up of characters
from specific character classes. The strings can be of fixed or variable length.
There are several built in character classes. You can also provide your own set
of characters to sample from. Below is the list of supported character classes:

Built In Classes
^^^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1

   * - class
     - description
   * - ascii
     - All valid ascii characters including control
   * - lower
     - ascii lowercase
   * - upper
     - ascii uppercase
   * - digits
     - Numbers 0 through 9
   * - letters
     - lowercase and uppercase
   * - word
     - letters + digits + '_'
   * - printable
     - All printable ascii chars including whitespace
   * - visible
     - All printable ascii chars excluding whitespace
   * - punctuation
     - local specific punctuation
   * - special
     - local specific punctuation
   * - hex
     - Hexadecimal digits including upper and lower case a-f
   * - hex-lower
     - Hexadecimal digits only including lower case a-f
   * - hex-upper
     - Hexadecimal digits only including upper case A-F

Prototype:

.. code-block:: python

    {
      "<field name>": {
        "type": "char_class":
        "data": <char_class_name>,
        or
        "type": "cc-<char_class_name>",
        or
        "type": "char_class":
        "data": <string with custom set of characters to sample from>
        or
        "type": "char_class":
        "data": [<char_class_name1>, <char_class_name2>, ..., <custom characters>]
        "config":{
          "exclude": <string of characters to exclude from output>,
          "escape": <string of characters to escape in output e.g. " -> \\", useful if non JSON output
          "escape_str": <string to use for escaping, default is \>
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
      "password": {
        "type": "char_class",
        "data": ["word", "special", "hex-lower", "M4$p3c!@l$@uc3"],
        "config": {
          "mean": 14,
          "stddev": 2,
          "min": 10,
          "max": 18,
          "exclude": ["-", "\""]
        }
      }
    }

.. code-block:: text

    $ datacraft -s spec.json -i 4 -r 1 -x -l off --format json
    {"password": "c1hbR&V!sYi4+Em"}
    {"password": "Z7Qd0AM>$f7'"}
    {"password": "9Bh8Z%6?ed4g"}
    {"password": "sqQ&I!Ucdp"}


.. code-block:: json

    {
      "one_to_five_digits:cc-digits?min=1&max=5": {}
    }

.. code-block:: text

    $ datacraft -s spec.json -i 4 -r 1 -x -l off --format json
    {"one_to_five_digits": "43040"}
    {"one_to_five_digits": "5"}
    {"one_to_five_digits": "6914"}
    {"one_to_five_digits": "752"}