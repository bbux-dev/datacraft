"""
Reference for holding configurations common to multiple fields

Prototype:

.. code-block:: python

    {
      "refs": {
        "<config ref name>": {
          "type": "configref",
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
          "configref": "tabs_config"
        }
      },
      "description": {
        "type": "csv",
        "config": {
          "column": 2,
          "configref": "tabs_config"
        }
      },
      "status_type:csv?configref=tabs_config&column=3": {},
      "refs": {
        "tabs_config": {
          "type": "configref",
          "config": {
            "datafile": "tabs.csv",
            "delimiter": "\t",
            "headers": true
          }
        }
      }
    }

"""
import datagen


@datagen.registry.types('configref')
def _configure_handler(_, __):
    """" Does nothing, just place holder """
