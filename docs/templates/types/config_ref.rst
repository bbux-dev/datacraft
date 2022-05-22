config_ref
----------

Reference for holding configurations common to multiple fields.

Prototype:

.. code-block:: python

    {
      "refs": {
        "<config ref name>": {
          "type": "config_ref",
          "config": {
            "key1": Any,
            ...
            "key2": Any
          }
        }
      }
    }

Examples:

.. code-block:: json

    {
      "status": {
        "type": "csv",
        "config": {
          "column": 1,
          "config_ref": "tabs_config"
        }
      },
      "description": {
        "type": "csv",
        "config": {
          "column": 2,
          "config_ref": "tabs_config"
        }
      },
      "status_type:csv?config_ref=tabs_config&column=3": {},
      "refs": {
        "tabs_config": {
          "type": "config_ref",
          "config": {
            "datafile": "tabs.csv",
            "delimiter": "\t",
            "headers": true
          }
        }
      }
    }