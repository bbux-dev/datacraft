"""
A standard uuid

Prototype:

.. code-block:: python

    {
      "<field name>": {
        "type": "uuid"
      }
    }


Examples:

.. code-block:: json

    {
      "id": {
        "type": "uuid"
      },
      "id_shorthand:uuid": {}
    }


"""
import uuid

import datagen

UUID_KEY = 'uuid'


class UuidSupplier(datagen.ValueSupplierInterface):
    """ Value Supplier for uuid type """

    def next(self, _):
        return str(uuid.uuid4())


@datagen.registry.schemas(UUID_KEY)
def _get_uuid_schema():
    """ get the schema for uuid type """
    return datagen.schemas.load(UUID_KEY)


@datagen.registry.types(UUID_KEY)
def _configure_supplier(_, __):
    """ configure the supplier for uuid types """
    return UuidSupplier()
