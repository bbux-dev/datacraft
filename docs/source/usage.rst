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

Spec Formats
------------

A Data Spec can be created in multiple formats.  The most common is the JSON syntax described above. Another format that
is supported is YAML:

.. code-block:: yaml

    ---
    id:
      type: uuid
    timestamp:
      type: date.iso
    count:
      type: rand_range
      data: [1,100]
      config:
        cast: int

There are also shorthand notations, see :doc:`fieldspecs` for more details.



Templating
----------

The datagen tool supports templating using the Jinja2 templating engine format.
To populate a template file or string with the generated values for each
iteration, pass the -t /path/to/template (or template string) arg to the
datagen command. We use the `Jinja2 <https://pypi.org/project/Jinja2/>`_
templating engine under the hood. The basic format is to put the field names in
{{ field name }} notation wherever they should be substituted. For example the
following is a template for bulk indexing data into Elasticsearch.

.. code-block:: json

   {"index": {"_index": "test", "_id": "{{ id }}"}}
   {"doc": {"name": "{{ name }}", "age": "{{ age }}", "gender": "{{ gender }}"}}

We could then create a spec to populate the id, name, age, and gender fields.
Such as:

.. code-block:: json

   {
     "id": {"type": "range", "data": [1, 10]},
     "gender": {"M": 0.48, "F": 0.52},
     "name": ["bob", "rob", "bobby", "bobo", "robert", "roberto", "bobby joe", "roby", "robi", "steve"],
     "age": {"type": "range", "data": [22, 44, 2]}
   }

When we run the tool we get the data populated for the template:

.. code-block:: shell

   datagen -s es-spec.json -t template.json -i 10 --log-level off -x
   { "index" : { "_index" : "test", "_id" : "1" } }
   { "doc" : {"name" : "bob", "age": "22", "gender": "F" } }
   { "index" : { "_index" : "test", "_id" : "2" } }
   { "doc" : {"name" : "rob", "age": "24", "gender": "F" } }
   { "index" : { "_index" : "test", "_id" : "3" } }
   { "doc" : {"name" : "bobby", "age": "26", "gender": "F" } }
   { "index" : { "_index" : "test", "_id" : "4" } }
   ...

It is also possible to do templating inline from the command line:

.. code-block:: shell

   datagen -s es-spec.json --format json -i 5  --log-level off -x --template '{{name}}: ({{age}}, {{gender}})'
   bob: (22, F)
   rob: (24, M)
   bobby: (26, M)
   bobo: (28, M)
   robert: (30, F)

Loops in Templates
~~~~~~~~~~~~~~~~~~

`Jinja2 Control Structures <https://jinja.palletsprojects.com/en/2.11.x/templates/#list-of-control-structures>`_
support looping. To provide multiple values to use in a loop use the ``count``
parameter. For example modifying the example from the Jinja2 documentation to
work with our tool:

.. code-block:: html

   <h1>Members</h1>
   <ul>
       {% for user in users %}
       <li>{{ user }}</li>
       {% endfor %}
   </ul>

If we use a regular spec such as ``{"users":["bob","bobby","rob"]}`` the
templating engine will not populate the template correctly since during each
iteration only a single name is returned as a string for the engine to process.

.. code-block:: html

   <h1>Members</h1>
   <ul>
       <li>b</li>
       <li>o</li>
       <li>b</li>
   </ul>

The engine requires collections to iterate over. A small change to our spec will
address this issue:

.. code-block:: json

   {"users?count=2": ["bob", "bobby", "rob"]}

Now we get

.. code-block:: html

   <h1>Members</h1>
   <ul>
       <li>bob</li>
       <li>bobby</li>
   </ul>

Dynamic Loop Counters
~~~~~~~~~~~~~~~~~~~~~

Another mechanism to do loops in Jinja2 is by using the python builtin ``range``
function. For example if we wanted a variable number of line items we could
create a template like the following:

.. code-block:: html

   <h1>Members</h1>
   <ul>
       {% for i in range(num_users | int) %}
       <li>{{ users[i] }}</li>
       {% endfor %}
   </ul>

Then we could update our spec to contain a ``num_users`` field:

.. code-block:: json

   {
     "users?count=4?sample=true": ["bob", "bobby", "rob", "roberta", "steve"],
     "num_users": {
       "2": 0.5,
       "3": 0.3,
       "4": 0.2
     }
   }

In the above spec the number of users created will be weighted so that half the
time there are two, and the other half there are three or four. NOTE: It is
important to make sure that the ``count`` param is equal to the maximum number
that will be indexed. If it is less, then there will be empty line items
whenever the num_users exceeds the count.
