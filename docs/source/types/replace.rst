replace
-------

Replace one or more parts of the output of a field or reference. Values to replace should be specified as strings.
Values to replace with should also be strings.

Prototype:

.. code-block:: python

    {
      "<field name>": {
        "type": "replace",
        "ref": "<field or ref to source value from>",
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
        "data": { "-": "" }
      }
    }

.. code-block:: text

    $ datacraft --spec uuid-spec.json -i 3 -r 1 -x -l off --format json
    {"id": "e809af25-bd85-4118-a5e9-cfdc953e172b", "remove_dashes": "1622e5cf2f334b81a90a6c031e0f78bf"}
    {"id": "2a98b892-bb73-49de-8186-fa7cb4510001", "remove_dashes": "9c1d22d6f6e544bb8c0d582c441a1c78"}
    {"id": "7986c789-1e5c-46f1-b5f1-a095f6a75209", "remove_dashes": "b50e914ea7994b6bb3194ce8c3402c8e"}


regex_replace
-------------

Replace one or more parts of the output of a field or reference using regular expressions to match the value strings.
Note that ``masked`` is an alias for this type.

Prototype:

.. code-block:: python

    {
      "<field name>": {
        "type": "regex_replace|masked",
        "ref": "<field or ref to source value from>",
        "data": {
          "<regex 1>": "<value to replace with 1>",
          ...
          "<regex N>": "<value to replace with N>",
        }
        OR
        "data": "<replace all values with this>
      }
    }


Examples:

This first example with take a 10 digit string of numbers and format it as a phone number. The double forward slash
allows the strings to be compiled into regular expressions.  Notice the \\N format for specifying the group capture
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

.. code-block:: text

    $ datacraft --spec phone-spec.json -i 4 -r 1 -x -l off --format json
    {"phone": "(773) 542-6190"}
    {"phone": "(632) 956-3481"}
    {"phone": "(575) 307-4587"}
    {"phone": "(279) 788-3403"}

Masked Example
^^^^^^^^^^^^^^

The ``masked`` type is an alias for ``regex_replace``. One mode for these type is to replace
all the values with a specified value for example:

.. code-block:: json

    {
      "masked_ssn": {
        "type": "masked",
        "ref": "ssn",
        "data": "NNN-NN-NNNN"
      },
      "age:rand_int_range": [18, 99],
      "refs": {
        "ssn": [
          "123-45-6789",
          "111-22-3333",
          "555-55-5555"
        ]
      }
    }

.. code-block:: text

    $  datacraft.exe -s ssn.json -i 3 --format csvh -x -l off
    masked_ssn,age
    NNN-NN-NNNN,40
    NNN-NN-NNNN,42
    NNN-NN-NNNN,73



