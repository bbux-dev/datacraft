.. py:currentmodule:: datacraft

.. _api:

Datacraft API
=============

The Datacraft API is can be used to generate data in a similar way to the command line tooling. Data Specs are defined
as dictionaries and follow the JSON based format and schemas. Most of the time you can copy a JSON spec from a file
and assign it to a variable and it will generate the same data as the command line ``datacraft`` tool.

Examples:
---------

`entries` and `generator`
^^^^^^^^^^^^^^^^^^^^^^^^^

By default, datacraft will generate dictionaries from the data specs. You can access a list of generated dictionaries
with the `datacraft.entries` function. If you hava a lot of data to generate, you will want to use a generator,
you can call `datacraft.generator` to access the data this way.

.. code-block:: python

    import datacraft

    spec = {
        "id": {"type": "uuid"},
        "timestamp": {"type": "date.iso.millis"},
        "handle": {"type": "cc-word", "config": { "min": 4, "max": 8, "prefix": "@" } }
    }

    print(*datacraft.entries(spec, 3), sep='\n')
    # {'id': '40bf8be1-23d2-4e93-9b8b-b37103c4b18c', 'timestamp': '2050-12-03T20:40:03.709', 'handle': '@WPNn'}
    # {'id': '3bb5789e-10d1-4ae3-ae61-e0682dad8ecf', 'timestamp': '2050-11-20T02:57:48.131', 'handle': '@kl1KUdtT'}
    # {'id': '474a439a-8582-46a2-84d6-58bfbfa10bca', 'timestamp': '2050-11-29T18:08:44.971', 'handle': '@XDvquPI'}

    # or if you prefer a generator
    for record in datacraft.generator(spec, 3_000_000):
        pass

`record_entries` and `record_generator`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you are using Data classes, you can tell datacraft to return your data as a data class using the `record_entries`
function.

.. code-block:: python

    import datacraft
    from dataclasses import dataclass

    @dataclass
    class Entry:
        id: str
        timestamp: str
        handle: str

    spec = {
        "id": {"type": "uuid"},
        "timestamp": {"type": "date.iso.millis"},
        "handle": {"type": "cc-word", "config": { "min": 4, "max": 8, "prefix": "@" } }
    }

    print(*datacraft.record_entries(Entry, spec, 3), sep='\n')
    # Entry(id='1a5d8158-f095-49f2-abaf-eef2e33b4075', timestamp='2024-07-11T18:58:30.376', handle='@g7Lu0Vd4')
    # Entry(id='f9e23a54-f9e8-4aa4-b3f5-aca45d89dd2c', timestamp='2024-07-21T20:00:32.290', handle='@kBCD7')
    # Entry(id='61239ab0-2d3d-420f-be01-15ec5d730fd1', timestamp='2024-07-04T13:53:07.322', handle='@GlWfzV6r')

    # or if you prefer a generator
    for record in datacraft.record_generator(Entry, spec, 3_000_000):
        pass

`registered_types` and `type_usage`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

There are some functions that can be helpful for getting the list of registered types as well as examples for
using them with the API.

.. code-block:: python

    import datacraft

    # List all registered types:
    datacraft.registered_types()
    # ['calculate', 'char_class', 'cc-ascii', 'cc-lower', '...', 'uuid', 'values', 'replace', 'regex_replace']

    # Print API usage for a specific type or types
    print(datacraft.type_usage('char_class', 'replace', '...'))
    # Example Output
    """
    -------------------------------------
    replace | API Example:

    import datacraft

    spec = {
     "field": {
       "type": "values",
       "data": ["foo", "bar", "baz"]
     },
     "replacement": {
       "type": "replace",
       "data": {"ba": "fi"},
       "ref": "field"
     }
    }

    print(*datacraft.entries(spec, 3), sep='\n')

    {'field': 'foo', 'replacement': 'foo'}
    {'field': 'bar', 'replacement': 'fir'}
    {'field': 'baz', 'replacement': 'fiz'}
    """

.. contents::
   :depth: 2

.. _core_clasess:

Core Classes
------------

.. _data_spec_class:

.. autoclass:: datacraft.DataSpec
   :members:

.. _value_supplier_interface:

.. autoclass:: datacraft.ValueSupplierInterface
   :members:

.. autoclass:: datacraft.Loader
   :members:

.. autoclass:: datacraft.Distribution
   :members:

.. autoclass:: datacraft.CasterInterface
   :members:

.. autoclass:: datacraft.RecordProcessor
   :members:

.. autoclass:: datacraft.OutputHandlerInterface
   :members:

.. autoclass:: datacraft.ResettableIterator
   :members:

.. _registry_decorators:

Registry Decorators
-------------------
.. autoclass:: datacraft.registries.Registry
   :members:

.. _datacraft_errors:

Datacraft Errors
----------------
.. autoclass:: datacraft.SpecException
   :members:

.. autoclass:: datacraft.SupplierException
   :members:

.. autoclass:: datacraft.ResourceError
   :members:

.. _supplier_module:

Suppliers Module
----------------
.. automodule:: datacraft.suppliers
   :members:

.. _builder_module:

Builder Module
--------------
.. automodule:: datacraft.builder
   :members:

.. _outputs_module:

Outputs Module
--------------
.. automodule:: datacraft.outputs
   :members:

.. _template_engines_module:

Template Engines
----------------
.. automodule:: datacraft.template_engines
   :members:

Spec Formatters
---------------
.. automodule:: datacraft.spec_formatters
   :members:

.. _spec_inference_module:

Data Spec Inference
-------------------
.. automodule:: datacraft.infer
   :members:
