Usage
=====

.. _installation:

Installation
------------

To use Datagen, first install it using pip:

.. code-block:: console

   (.venv) $ pip install git+https://github.com/bbux-dev/datagen.git

   (.venv) $ datagen -h # for command line usage

Generating Data
----------------

The Datagen tool uses Data Specs to construct records. If for example, we need a list of uuids:

.. code-block:: console

    $ datagen --inline "{demo: {type: uuid}}" --log-level off -i 5
    d1e027bd-0836-4a07-b073-9d8c33aa432a
    258452c2-61a6-4764-96b9-a3b9b22f42c2
    47e45cd1-319a-41af-80b8-73987ca82fea
    3f9843a7-d8a4-45e5-b36b-88c4b5f88cd8
    a4704ff0-3305-456e-9e51-93327d1459d3

This command uses an inline yaml syntax to specify a single field called ``demo`` that has a type of ``uuid``. We tell
the datagen tool to turn off logging and to generate 5 records from this inline spec. The default is for output to be
printed to the console. Inline Data Specs can be useful for testing and development. Most Data Specs will be in JSON or
YAML files. Use the ``--debug-spec`` flag to dump the inline spec out as JSON for easier additions and configuration
changes:

.. code-block:: console

    $ datagen --inline "{demo: {type: uuid}}" --log-level off --debug-spec > demo.json
    $ cat demo.json
    {
        "demo": {
            "type": "uuid"
        }
    }
    $ datagen -s demo.json --log-level off -i 5
    5c4b45ed-4334-48bf-90c6-a3566a3af80b
    8b8bf4fa-f931-46fe-9f8c-f7317e59fbfe
    b2832228-e426-4fe5-a518-3a32d1dede2e
    793fc068-4a4c-4be5-86f5-b18f690eef95
    973cc430-7d24-43d1-9fba-5adfdb0ae8d6

Generating Records
------------------

Many times we will want to generate some kind of record with more than one field in it.  A common format for generating
records is to output them as JSON.  There is a ``--format`` flag that supports multiple output formats.  If we modify
our example above to the following:

.. code-block:: json

    {
        "id": {"type": "uuid"},
        "timestamp": {"type": "date.iso"},
        "count": {"type": "rand_range", "data": [1,100], "config": {"cast": "int"}}
    }

Here we define the three fields of our record: ``id``, ``timestamp``, and ``count``. The portion after the name is
called a Field Spec. This defines the type of data the field consists of and how it should be generated. The ``id``
field is a ``uuid`` just like the previous example.  The ``timestamp`` is a ISO 8601 date and the ``count`` is a random
number between 1 and 100 that is cast to an integer. If we run this spec and specify the ``--format json`` flag:

.. code-block:: console

    $ datagen -s demo.json --log-level off -i 5 --format json -x
    {"id": "706bf38c-02a8-4087-bf41-62cdf4963f0b", "timestamp": "2021-11-30T05:21:14", "count": 59}
    {"id": "d96bad3e-45c3-424e-9d4e-1233f9ed6ab5", "timestamp": "2021-11-09T20:21:03", "count": 61}
    {"id": "ff3b8d87-ab3d-4ebe-af35-a081ee5098b5", "timestamp": "2021-11-05T08:24:05", "count": 36}
    {"id": "b6fbd17f-286b-4d58-aede-01901ae7a1d7", "timestamp": "2021-11-10T09:37:47", "count": 16}
    {"id": "f4923efa-28c5-424a-8560-49914dd2b2ac", "timestamp": "2021-11-19T17:28:13", "count": 29}

There are other output formats available and a mechanism to register custom formatters. If a csv file is more suited
for your needs:

.. code-block:: console

    $ datagen -s demo.json --log-level off -i 5 --format csv -x
    1ad0b69b-0843-4c0d-90a3-d7b77574a3af,2021-11-21T21:24:44,2
    b504d688-6f02-4d41-8b05-f55a681b940a,2021-11-14T15:29:59,76
    11502944-dacb-4812-8d73-e4ba693f2c05,2021-11-24T00:17:55,98
    8370f761-66b1-488e-9327-92a7b8d795b0,2021-11-08T02:55:11,4
    ff3d9f36-6560-4f26-8627-e18dea66e26b,2021-11-15T07:33:42,89