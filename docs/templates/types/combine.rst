combine
-------

A combine Field Spec is used to concatenate or append two or more fields or reference to one another.
There are two combine types: ``combine`` and ``combine-list``.

combine
^^^^^^^

Prototype:

.. code-block:: python

    {
      "<field name>": {
        "type": "combine",
        "fields": ["valid field name1", "valid field name2"],
        OR
        "refs": ["valid ref1", "valid ref2"],
        "config": {
          "join_with": "<optional string to use to join fields or refs, default is none>"
        }
      }
    }

Examples:

.. code-block:: json

    {
      "combine": {
        "type": "combine",
        "refs": ["first", "last"],
        "config": {
          "join_with": " "
        }
      },
      "refs": {
        "first": {
          "type": "values",
          "data": ["zebra", "hedgehog", "llama", "flamingo"]
        },
        "last": {
          "type": "values",
          "data": ["jones", "smith", "williams"]
        }
      }
    }

combine-list
^^^^^^^^^^^^

Prototype:

.. code-block:: python

    {
      "<field name>": {
        "type": "combine-list",
        "refs": [
          ["valid ref1", "valid ref2"],
          ["valid ref1", "valid ref2", "valid_ref3", ...], ...
          ["another_ref", "one_more_ref"]
        ],
        "config": {
          "join_with": "<optional string to use to join fields or refs, default is none>"
        }
      }
    }

Examples:

.. code-block:: json

    {
      "full_name": {
        "type": "combine-list",
        "refs": [
          ["first", "last"],
          ["first", "middle", "last"],
          ["first", "middle_initial", "last"]
        ],
        "config": {
          "join_with": " "
        }
      },
      "refs": {
        "first": {
          "type": "values",
          "data": ["zebra", "hedgehog", "llama", "flamingo"]
        },
        "last": {
          "type": "values",
          "data": ["jones", "smith", "williams"]
        },
        "middle": {
          "type": "values",
          "data": ["cloud", "sage", "river"]
        },
        "middle_initial": {
          "type": "values",
          "data": {"a": 0.3, "m": 0.3, "j": 0.1, "l": 0.1, "e": 0.1, "w": 0.1}
        }
      }
    }
