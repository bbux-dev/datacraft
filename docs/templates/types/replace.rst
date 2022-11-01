replace
-------

Replace one or more parts of the output of a field or reference. Values to replace should be specified as strings.
Values to replace with should also be strings.

Prototype:

.. code-block:: python

    {
      "<field name>": {
        "type": "replace",
        "data": {
          "<value to replace 1>": "<value to replace with 1>",
          ...
          "<value to replace N>": "<value to replace with N>",
        }
      }
    }


Examples:

.. code-block:: json

    {
      "id": {
        "type": "uuid"
      },
      "remove_dashes": {
        "type": "replace",
        "ref": "id",
        "data": { "-", "" }
      }
    }

regex_replace
-------------

Replace one or more parts of the output of a field or reference using regular expressions to match the value strings.

Prototype:

.. code-block:: python

    {
      "<field name>": {
        "type": "regex_replace",
        "data": {
          "<value to replace 1>": "<value to replace with 1>",
          ...
          "<value to replace N>": "<value to replace with N>",
        }
      }
    }


Examples:

This first example with take a 10 digit string of numbers and format it as a phone number. The double forward slash
allows the strings to be compiled into regular expressions.  Notice the \N format for specifying the group capture
replacement.

.. code-block:: json

    {
      "phone": {
        "type": "regex_replace",
        "ref": "ten_digits",
        "data": {
          "^(\\d{3})(\\d{3})(\\d{4})": "(\\1) \\2-\\3"
        }
      },
      "refs": {
        "ten_digits": {
          "type": "cc-digits",
          "config": {
            "count": 10,
            "buffer": true
          }
        }
      }
    }