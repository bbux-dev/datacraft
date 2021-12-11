nested
------

Nested types are used to create fields that contain subfields. Nested types can
also contain nested fields to allow multiple levels of nesting. Use the ``nested``
type to generate a field that contains subfields. The subfields are defined in
the ``fields`` element of the nested spec. The ``fields`` element will be treated
like a top level DataSpec and has access to the ``refs`` and other elements of the
root.

Prototype:

.. code-block:: python

    {
      "<field name>": {
        "type": "nested",
        "config": {
          "count": "Values Spec for Counts, default is 1"
        },
        "fields": {
          "<sub field one>": { spec definition here },
          "<sub field two>": { spec definition here },
          ...
        },
        "field_groups": <field groups format>
      }
    }

Examples:

.. code-block:: json

    {
      "id": {
        "type": "uuid"
      },
      "user": {
        "type": "nested",
        "fields": {
          "user_id": {
            "type": "uuid"
          },
          "geo": {
            "type": "nested",
            "fields": {
              "place_id:cc-digits?mean=5": {},
              "coordinates:geo.pair?as_list=true": {}
            }
          }
        }
      }
    }

The same spec in a slightly more compact format

.. code-block:: json

    {
      "id:uuid": {},
      "user:nested": {
        "fields": {
          "user_id:uuid": {},
          "geo:nested": {
            "fields": {
              "place_id:cc-digits?mean=5": {},
              "coordinates:geo.pair?as_list=true": {}
            }
          }
        }
      }
    }

Generates the following structure

.. code-block:: shell

    datacraft -s tweet-geo.json --log-level off -x -i 1 --format json-pretty

.. code-block:: json

    {
        "id": "68092478-2234-41aa-bcc6-e679950770d7",
        "user": {
            "user_id": "93b3c62e-76ad-4272-b3c1-b434be2c8c30",
            "geo": {
                "place_id": "5104987632",
                "coordinates": [
                    -93.0759,
                    68.2469
                ]
            }
        }
    }
