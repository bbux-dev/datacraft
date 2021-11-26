Usage
=====

.. _installation:

Installation
------------
To use Datagen, first install it using pip:

.. code-block:: text

   (.venv) $ pip install git+https://github.com/bbux-dev/datagen.git

   (.venv) $ datagen -h # for command line usage

Generating Data
----------------

The Datagen tool uses what we call Data Specs to construct records. A Data Spec consists of one or more Field Specs.
Each Field Spec will generate the values for one field. If for example, you need a list of uuids, you can run the
command below.

.. code-block:: text

    $ datagen --inline "{demo: {type: uuid}}" --log-level off -i 5
    d1e027bd-0836-4a07-b073-9d8c33aa432a
    258452c2-61a6-4764-96b9-a3b9b22f42c2
    47e45cd1-319a-41af-80b8-73987ca82fea
    3f9843a7-d8a4-45e5-b36b-88c4b5f88cd8
    a4704ff0-3305-456e-9e51-93327d1459d3

This command uses an inline yaml syntax for the Data Spec. The spec consists of a single field ``demo``. The value
for the demo key is the Field Spec. The Field Spec has a type of ``uuid``, which is all that is needed for this spec.
The command tells the datagen tool to turn off logging and to generate 5 records from this inline spec. The default
is for output to be printed to the console. Inline Data Specs can be useful for testing and development. Most Data
Specs will be in JSON or YAML files. Use the ``--debug-spec`` flag to dump the inline spec out as JSON for easier
additions and configuration changes. Use the ``--debug-spec-yaml`` flag if you prefer to work with the more compact
YAML format.

.. code-block:: text

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

.. code-block:: shell

    $ datagen -s demo.json --log-level off -i 5 --format json -x
    {"id": "706bf38c-02a8-4087-bf41-62cdf4963f0b", "timestamp": "2021-11-30T05:21:14", "count": 59}
    {"id": "d96bad3e-45c3-424e-9d4e-1233f9ed6ab5", "timestamp": "2021-11-09T20:21:03", "count": 61}
    {"id": "ff3b8d87-ab3d-4ebe-af35-a081ee5098b5", "timestamp": "2021-11-05T08:24:05", "count": 36}
    {"id": "b6fbd17f-286b-4d58-aede-01901ae7a1d7", "timestamp": "2021-11-10T09:37:47", "count": 16}
    {"id": "f4923efa-28c5-424a-8560-49914dd2b2ac", "timestamp": "2021-11-19T17:28:13", "count": 29}

There are other output formats available and a mechanism to register custom formatters. If a csv file is more suited
for your needs:

.. code-block:: shell

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

There are also shorthand notations, see :doc:`fieldspecs` for more details. A spec in one format can be converted to
the other by using the command line ``--debug-spec`` and ``--debug-spec-yaml`` flags. ``--debug-spec`` will write out
the JSON version, and ``--debug-spec-yaml`` will write out the YAML version. These commands will output the full
format for the specs and any shorthand notations will be pushed down into the field spec. For example:

.. code-block:: json

    {
      "foo:cc-word?mean=5&min=3&max=12": {}
    }

Will become

.. tabs::

   .. tab:: JSON

      .. code-block:: json

        {
          "foo": {
            "type": "cc-word",
            "config": {
              "mean": "5",
              "min": "3",
              "max": "12"
            }
          }
        }

   .. tab:: YAML

      .. code-block:: yaml

        foo:
          type: cc-word
          config:
            mean: '5'
            min: '3'
            max: '12'


Refs
----------

There is a special section in the Data Spec called ``refs``.  This is short for references and is where a Field
Spec can be defined outside of a field.  Field Specs can then point to a ref to supply values it can use for the data
generation process.  The simplest example of this is the ``combine`` type:

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

Here the combine type takes a refs argument that specifies the name of two references to combine the values of. There
is also a ``ref`` type. This is useful for making Data Specs easier to read by segmenting the structures into smaller
pieces.  This is particularly useful with ``nested`` types:

.. code-block:: json

    {
      "outer": {
        "type": "nested",
        "fields": {
          "simple_uuid": { "type": "uuid" },
          "complex_value:ref": "COMPLEX_VALUE_DEFINED"
        }
      },
      "refs": {
        "COMPLEX_VALUE_DEFINED": {
          "type": "rand_range",
          "data": [0, 42],
          "config": {
            "prefix": "~",
            "suffix": " microns per second",
            "quote": "'",
            "precision": 3
          }
        }
      }
    }

In this example the ``complex_value`` field has a lot going on.  To simplify the specification for the ``outer``
field, the spec uses a type of ``ref`` to point to the ``COMPLEX_VALUE_DEFINED`` reference.  Notice that the
shorthand notation of ``<field name>:<type>`` is used to simplify the spec.  The full spec version of this can be seen
with the ``--debug-spec`` command line argument. If we run this spec from the command line:

.. code-block:: shell

    $ datagen -s refs_type.json -i 3 --log-level off --format json -x
    {"outer": {"simple_uuid": "c77a5bee-83bb-4bae-a8e8-21be735f73c9", "complex_value": "'~4.028 microns per second'"}}
    {"outer": {"simple_uuid": "5d27eb03-c5a3-4167-9dd1-56c1f0b5a49c", "complex_value": "'~21.221 microns per second'"}}
    {"outer": {"simple_uuid": "6fa92f9f-d3ac-4118-ad2f-89b73bafb7c5", "complex_value": "'~27.432 microns per second'"}}


Templating
----------

The datagen tool supports templating using the Jinja2 templating engine format. To populate a template file or string
with the generated values for each iteration, pass the -t /path/to/template (or template string) arg to the datagen
command. We use the `Jinja2 <https://pypi.org/project/Jinja2/>`_ templating engine under the hood. The basic format
is to put the field names in {{ field name }} notation wherever they should be substituted. For example the following
is a template for bulk indexing data into Elasticsearch.

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

   datagen -s es-spec.json -i 5 --log-level off -x --template '{{name}}: ({{age}}, {{gender}})'
   bob: (22, F)
   rob: (24, M)
   bobby: (26, M)
   bobo: (28, M)
   robert: (30, F)

Loops in Templates
^^^^^^^^^^^^^^^^^^

`Jinja2 Control Structures <https://jinja.palletsprojects.com/en/2.11.x/templates/#list-of-control-structures>`_
support looping. To provide multiple values to use in a loop use the ``count`` parameter. Modifying the
example from the Jinja2 documentation to work with datagen:

.. code-block:: html

   <h1>Members</h1>
   <ul>
       {% for user in users %}
       <li>{{ user }}</li>
       {% endfor %}
   </ul>

If a regular spec is used such as ``{"users":["bob","bobby","rob"]}`` the templating engine will not populate the
template correctly since during each iteration only a single name is returned as a string for the engine to process.

.. code-block:: html

   <h1>Members</h1>
   <ul>
       <li>b</li>
       <li>o</li>
       <li>b</li>
   </ul>

The engine requires collections to iterate over. A small change to the spec will address this issue:

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
^^^^^^^^^^^^^^^^^^^^^

Another mechanism to do loops in Jinja2 is by using the python builtin ``range`` function. If a variable
number of line items was desired, you could create a template like the following:

.. code-block:: html

   <h1>Members</h1>
   <ul>
       {% for i in range(num_users | int) %}
       <li>{{ users[i] }}</li>
       {% endfor %}
   </ul>

The spec could then be updated to contain a ``num_users`` field:

.. code-block:: json

    {
      "users": {
        "type": "values",
        "data": ["bob", "bobby", "rob", "roberta", "steve"],
        "config": {
          "count": "4",
          "sample": "true"
        }
      },
      "num_users": {
        "type": "values",
        "data": {
          "2": 0.5,
          "3": 0.3,
          "4": 0.2
        }
      }
    }

In the spec above, the number of users created will be weighted so that half the time there are two, and the other
half there are three or four. NOTE: It is important to make sure that the ``count`` param is equal to the maximum number
that will be indexed. If it is less, then there will be empty line items whenever the num_users exceeds the count.

.. _field_groups:

Field Groups
------------

Field groups provide a mechanism to generate different subsets of the defined fields together. This can be useful
when modeling data that contains field that are not present in all records. There are several formats that are
supported for Field Groups. Field Groups are defined in a root section of the document named ``field_groups`` or as
part of ``nested`` Field Specs. Below is an example spec with no ``field_groups`` defined.

.. code-block:: json

   {
     "id": {"type": "range", "data": [1, 100]},
     "name": ["Fido", "Fluffy", "Bandit", "Bingo", "Champ", "Chief", "Buster", "Lucky"],
     "tag": {
       "Affectionate": 0.3, "Agreeable": 0.1, "Charming": 0.1,
       "Energetic": 0.2, "Friendly": 0.4, "Loyal": 0.3,
       "Aloof": 0.1
     }
   }

If the tag field was only present in 50% of the data, we would want to be able to adjust the output to match this.
Here is an updated version of the spec with the ``field_groups`` specified to give the 50/50 output. This uses the
first form of the ``field_groups`` a List of Lists of field names to output together.

.. code-block:: json

   {
     "id": {"type": "range", "data": [1, 100]},
     "name": ["Fido", "Fluffy", "Bandit", "Bingo", "Champ", "Chief", "Buster", "Lucky"],
     "tag": {
       "Affectionate": 0.3, "Agreeable": 0.1, "Charming": 0.1,
       "Energetic": 0.2, "Friendly": 0.4, "Loyal": 0.3,
       "Aloof": 0.1
     },
     "field_groups": [
       ["id", "name"],
       ["id", "name", "tag"]
     ]
   }

If more precise weightings are needed, you can use the second format where a weight is specified for each field group
along with the fields that should be output together.

.. code-block:: json

   {
     "id": "...",
     "name": "...",
     "tag": "...",
     "field_groups": {
       "0.3": ["id", "name"],
       "0.7": ["id", "name", "tag"]
     }
   }

The keys of the ``field_groups`` must all be floating point numbers as strings.

Running this example:

.. code-block:: shell

   $ datagen -s pets.json -i 10 -l off -x --format json
   {"id": 1, "name": "Fido"}
   {"id": 2, "name": "Fluffy", "tag": "Agreeable"}
   {"id": 3, "name": "Bandit", "tag": "Affectionate"}
   {"id": 4, "name": "Bingo"}
   {"id": 5, "name": "Champ", "tag": "Loyal"}
   {"id": 6, "name": "Chief"}
   {"id": 7, "name": "Buster", "tag": "Friendly"}
   {"id": 8, "name": "Lucky", "tag": "Loyal"}
   {"id": 9, "name": "Fido", "tag": "Aloof"}
   {"id": 10, "name": "Fluffy", "tag": "Affectionate"}

The final form is a variation on form 2. Here the ``field_groups`` value is a dictionary of name to fields list. This
acts like the first form and the sets of fields are rotated through in turn.

.. code-block:: json

   {
     "id": "...",
     "name": "...",
     "tag": "...",
     "field_groups": {
       "no_tag":   ["id", "name"],
       "with_tag": ["id", "name", "tag"]
     }
   }

CSV Inputs
----------

Instead of hard coding large numbers of values into a Data Spec, these can be externalized using the one of the
:ref:`csv<csv_core_types>` types. This requires a ``-d`` or ``--datadir`` argument when running from the command line
to specify where the referenced csv files live. For example:

.. code-block:: json

    {
      "cities": {
        "type": "csv",
        "config": {
          "column": 1,
          "datafile": "cities.csv",
          "sample": true
        }
      }
    }

.. code-block:: shell

    datagen -s spec.json -d dir_with_csvs --log-level off -i 3
    New York
    San Diego
    Springfield

Common CSV Configs
^^^^^^^^^^^^^^^^^^

If more than one field is used from a csv file, it may be useful to create a :ref:`config_ref<config_ref_core_types>`
to hold the common configurations for the fields. Below there are two fields that use the same csv file to supply
their values. The common configurations for the csv file are placed in the refs section in a ref titled
``http_csv_config``. The status and status_name fields now only have two configuration parameters: ``column`` and
``config_ref``.

.. code-block:: json

    {
      "status:csv": {
        "config": {
          "column": 1,
          "config_ref": "http_csv_config"
        }
      },
      "status_name:csv": {
        "config": {
          "column": 2,
          "config_ref": "http_csv_config"
        }
      },
      "refs": {
        "http_csv_config": {
          "type": "config_ref",
          "config": {
            "datafile": "http_codes.csv",
            "headers": true,
            "delimiter": "\\t"
            "sample_rows": true
          }
        }
      }
    }

Row Level Sampling
^^^^^^^^^^^^^^^^^^

By default, the rows of a CSV file are iterated through in order.  It is possible to enable sampling on a per column
basis by setting the ``sample`` config value to one of on, yes, or true. If you want to sample a csv file at the row
level, you need to set the config param ``sample_rows`` to one of on, yes, or true. If this value is set for the
first csv field from the same file defined, it will be inherited by the rest. If it is not configured on the first
field, it will not be enabled, even if set on a later field. It is safest to define the field in a config_ref that all
of the fields share, as illustrated in the above example.

Processing Large CSVs
^^^^^^^^^^^^^^^^^^^^^

There are Field Specs that support using csv data to feed the data generation process. If the input CSV file is very
large, not all features will be supported. You will not be able to set sampling to true or use a field count > 1. The
maximum number of iterations will be equal to the size of the smallest number of lines for all the large input CSV
files. The current size threshold is set to 250 MB. So, if you are using two different csv files as inputs and one is
300 MB with 5 million entries and another is 500 MB with 2 million entries, you will be limited to 2 million
iterations before an exception will be raised and processing will cease., You can override the default size limit on
the command line by using the ``--set-default`` flag. Example:

.. code-block:: shell

   datagen --set-default large_csv_size_mb=1024 --datadir path/to/large.csv ...

More efficient processing using csv_select
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A common process is to select subsets of the columns from a csv file to use in the data generation process. The
``csv_select`` type makes this more efficient than using the standard ``csv`` type. Below is an example that will
Convert data from the `Geonames <http://www.geonames.org/>`_ `allCountries.zip <http://download.geonames
.org/export/dump/allCountries.zip>`_ dataset by selecting a subset of the columns from the tab delimited file.

.. code-block:: yaml

   ---
   placeholder:
     type: csv_select
     data:
       geonameid: 1
       name: 2
       latitude: 5
       longitude: 6
       country_code: 9
       population: 15
     config:
       datafile: allCountries.txt
       headers: no
       delimiter: "\t"

Running this spec would produce:

.. code-block:: shell

   $ datagen --spec csv-select.yaml -i 5 --datadir ./data --format json --log-level off -x
   {"geonameid": "2986043", "name": "Pic de Font Blanca", "latitude": "42.64991", "longitude": "1.53335", "country_code": "AD", "population": "0"}
   {"geonameid": "2994701", "name": "Roc M\u00e9l\u00e9", "latitude": "42.58765", "longitude": "1.74028", "country_code": "AD", "population": "0"}
   {"geonameid": "3007683", "name": "Pic des Langounelles", "latitude": "42.61203", "longitude": "1.47364", "country_code": "AD", "population": "0"}
   {"geonameid": "3017832", "name": "Pic de les Abelletes", "latitude": "42.52535", "longitude": "1.73343", "country_code": "AD", "population": "0"}
   {"geonameid": "3017833", "name": "Estany de les Abelletes", "latitude": "42.52915", "longitude": "1.73362", "country_code": "AD", "population": "0"}

.. _custom_code:

Custom Code Loading and Schemas
-------------------------------

There are a lot of types of data that are not generated with this tool. Instead of adding them all, there is a
mechanism to bring your own data suppliers. We make use of the handy `catalogue <https://pypi.org/project/catalogue/>`_
package to allow auto discovery of custom functions using decorators. Use the ``@datagen.registry.types('<type key>')``
to register a function that will create a :ref:`Value Supplier<value_supplier_interface>` for the supplied Field
Spec. Below is an example of a custom class which reverses the output of another supplier. This same operation could
also be done with a :ref:`custom caster<custom_value_casters>`

To supply custom code to the tool use the ``-c`` or ``--code`` arguments. One or more module files can be imported.

.. tabs::

   .. tab:: Custom Code

      .. code-block:: python

         import datagen

         class ReverseStringSupplier(datagen.ValueSupplierInterface):
             def __init__(self, wrapped):
                 self.wrapped = wrapped

             def next(self, iteration):
                 # value from the wrapped supplier
                 value = str(self.wrapped.next(iteration))
                 # python way to reverse a string, hehe
                 return value[::-1]

         @datagen.registry.types('reverse_string')
         def configure_supplier(field_spec: dict,
                                loader: datagen.Loader) -> datagen.ValueSupplierInterface:
             # load the supplier for the given ref
             key = field_spec.get('ref')
             wrapped = loader.get(key)
             # wrap this with our custom reverse string supplier
             return ReverseStringSupplier(wrapped)

         @datagen.registry.schemas('reverse_string')
         def get_reverse_string_schema():
             return {
                 "$schema": "http://json-schema.org/draft-07/schema#",
                 "$id": "reverse_string.schema.json",
                 "type": "object",
                 "required": ["type", "ref"],
                 "properties": {
                     "type": {"type": "string", "pattern": "^reverse_string$"},
                     "ref": {"type": "string"}
                 }
             }

   .. tab:: Data Spec

      .. code-block::

         {
           "backwards": {
             "type": "reverse_string",
             "ref": "ANIMALS"
           },
           "refs": {
             "ANIMALS": {
               "type": "values",
               "data": ["zebra", "hedgehog", "llama", "flamingo"]
             }
           }
         }

   .. tab:: Command and Output

      .. code-block:: shell

         .datagen -s reverse-spec.json -i 4 -c custom.py another.py -x --log-level off
         arbez
         gohegdeh
         amall
         ognimalf

Now when we see a type of "reverse_string" like in the example below, we will use the given function to configure the
supplier for it. The function name for the decorated function is arbitrary, but the signature must match. The signature
for the Value Supplier is required to match the interface and have a single ``next(iteration)`` method that returns
the next value for the given iteration. You can also optionally register a schema for the type. The schema will be
applied to the spec if the ``--strict`` command line flag is specified, otherwise you will have to perform your own
validation in your code.





Programmatic Usage
------------------

Building Specs
^^^^^^^^^^^^^^

The :ref:`datagen.builder<builder_module>` module contains tools that can be used to programmatically generate Data
Specs. This may be easier for some who are not as familiar with JSON or prefer to manage their structures in code.
The core object is the ``Builder``. You can add fields, refs, and field groups to this. Each of the core field types
has a builder function that will generate a Field Spec for it. See example below.

These examples can be used to generate email addresses.  The first example uses the raw API to build up the spec. The
second uses a dictionary that mirrors the JSON format.

.. code-block:: python

   import datagen

   animal_names = ['zebra', 'hedgehog', 'llama', 'flamingo']
   action_list = ['fling', 'jump', 'launch', 'dispatch']
   domain_weights = {
       "gmail.com": 0.6,
       "yahoo.com": 0.3,
       "hotmail.com": 0.1
   }
   # for building the final spec
   spec_builder = datagen.spec_builder()
   # for building the references, is it self also a Builder, but with no refs
   refs = spec_builder.refs()
   # info for each reference added
   domains = refs.values('DOMAINS', data=domain_weights)
   animals = refs.values('ANIMALS', data=animal_names)
   actions = refs.values('ACTIONS', data=action_list, sample=True)
   # combines ANIMALS and ACTIONS with an _
   handles = refs.combine('HANDLE', refs=[animals, actions], join_with='_')

   spec_builder.combine('email', refs=[handles, domains], join_with='@')

   spec = spec_builder.build()

   # print single generated record
   print(next(spec.generator(1)))
   #{'email': 'zebra_dispatch@gmail.com'}


An alternative is to have a spec as a dictionary that mirrors the JSON format:

.. code-block:: python

   import datagen

   raw_spec = {
     "email": {
       "type": "combine",
       "refs": ["HANDLE", "DOMAINS"],
       "config": {"join_with": "@"}
     },
     "refs": {
       "HANDLE": {
         "type": "combine",
         "refs": ["ANIMALS", "ACTIONS"],
         "config": {"join_with": "_"}
       },
       "ANIMALS": {
         "type": "values",
         "data": ["zebra", "hedgehog", "llama", "flamingo"]
       },
       "ACTIONS?sample=true": {
         "type": "values",
         "data": ["fling", "jump", "launch", "dispatch"]
       },
       "DOMAINS": {
         "type": "values",
         "data": {"gmail.com": 0.6, "yahoo.com": 0.3, "hotmail.com": 0.1}
       }
     }
   }

   spec = datagen.parse_spec(raw_spec)

   # print single generated record
   print(next(spec.generator(1)))
   #{'email': 'zebra_fling@gmail.com'}


Record Generator
^^^^^^^^^^^^^^^^

The :ref:`spec.generator<data_spec_class>` function will create a python generator that can be used to incrementally
generate the records from the DataSpec.

Example:

.. code-block:: python

    import datagen

    name_list = ['bob', 'bobby', 'robert', 'bobo']
    builder = datagen.spec_builder()
    spec = builder.values('name', name_list).to_spec()

    template = 'Name: {{ name }}'
    # need this to apply the data to the template
    processor = datagen.outputs.processor(template=template)

    generator = spec.generator(
       iterations=5,
       processor=processor)

    single_record = next(generator)
    # 'Name: bob'
    remaining_records = list(generator)  # five iterations wraps around to first
    # ['Name: bobby', 'Name: robert', 'Name: bobo', 'Name: bob']


REST Server
-----------

Datagen comes with a lightweight Flask server to use to retrieve generated data. Use the ``--server`` with the optional
``--server-endpoint /someendpoint`` flags to launch this server.  The default end point will be found at
http://127.0.0.1:5000/data. If using a template, each call to the endpoint will return the results of applying a
single record to the template data. If you specify one of the ``--format`` flags, the formatted record will be returned.
If neither a formatter or a template are applied, the record for each itertion will be returned.

Server side of the transaction, serving up data formatted using the json-pretty formatter. The records contain a
uuid and a timestamp field.

.. code-block:: shell

    $ datagen --inline "{id:uuid: {}, ts:date: {}}" -i 2 --log-level debug --format json-pretty --server
     * Serving Flask app 'datagen.server' (lazy loading)
     * Environment: production
       WARNING: This is a development server. Do not use it in a production deployment.
       Use a production WSGI server instead.
     * Debug mode: off
     * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
    127.0.0.1 - - [23/Nov/2021 20:48:41] "GET /data HTTP/1.1" 200 -
    127.0.0.1 - - [23/Nov/2021 20:48:44] "GET /data HTTP/1.1" 200 -
    No more iterations available
    127.0.0.1 - - [23/Nov/2021 20:48:46] "GET /data HTTP/1.1" 204 -

Client side of the transaction

.. code-block:: bash

    $ curl -s -w "\n%{http_code}\n%" http://127.0.0.1:5000/data
    {
        "id": "505b62d6-0d21-4965-92a7-f719463fdb0b",
        "ts": "03-12-2050"
    }
    200
    $ curl -s -w "\n%{http_code}\n%" http://127.0.0.1:5000/data
    {
        "id": "51e5d07b-4d46-48d7-9523-e1e0ecf723f3",
        "ts": "09-12-2050"
    }
    200
    $ curl -s -w "\n%{http_code}\n%" http://127.0.0.1:5000/data

    204

In this exchange, three requests are made.  The first two return the generated data formatted. The third returns a 204
or No Content response code.  This is because the number of iterations was set to 2.