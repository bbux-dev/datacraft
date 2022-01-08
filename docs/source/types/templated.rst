templated
---------

A templated Field Spec is used to create strings by injecting the values from other fields into them. The other
fields must be defined.  The values can come from references or other defined fields. Use the jinja2 ``{{ field }}``
syntax to signify where the field should be injected.

Prototype:

.. code-block:: python

    {
      "<field name>": {
        "type": "templated",
        "data": "string with {{ jinja2 }} syntax fields",
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
      "templated": {
        "type": "templated",
        "data": "Mozilla/5.0 ({{ system }}) {{ platform }}",
        "refs": ["first", "last"],
      },
      "refs": {
        "system": {
          "type": "values",
          "data": [
            "(Windows NT 6.1; Win64; x64; rv:47.0)",
            "(Macintosh; Intel Mac OS X x.y; rv:42.0)"
          ]
        },
        "platform": {
          "type": "values",
          "data": ["Gecko/20100101 Firefox/47.0", "Gecko/20100101 Firefox/42.0"]
        }
      }
    }