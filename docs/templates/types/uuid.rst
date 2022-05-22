uuid
----

A standard uuid

Prototype:

.. code-block:: python

    {
      "<field name>": {
        "type": "uuid",
        "config": {
          "variant": 1, 3, 4, or 5, default is 4, optional
        }
      }
    }


Examples:

.. code-block:: json

    {
      "id": {
        "type": "uuid"
      },
      "id_shorthand:uuid": {}
      "id_variant3" {
        "type": "uuid",
        "config": {
          "variant": 3
        }
      }
    }
