Usage
=====

.. _installation:

Installation
------------
To use Datacraft, first install it using pip:

.. code-block:: text

   (.venv) $ pip install datacraft

   (.venv) $ datacraft -h # for command line usage

Generating Data
----------------

The Datacraft tool uses what we call Data Specs to construct records. A Data Spec consists of one or more Field Specs.
Each Field Spec will generate the values for one field. If for example, you need a list of uuids, you can run the
command below.

.. code-block:: text

    $ datacraft --inline "{demo: {type: uuid}}" --log-level off -i 5
    d1e027bd-0836-4a07-b073-9d8c33aa432a
    258452c2-61a6-4764-96b9-a3b9b22f42c2
    47e45cd1-319a-41af-80b8-73987ca82fea
    3f9843a7-d8a4-45e5-b36b-88c4b5f88cd8
    a4704ff0-3305-456e-9e51-93327d1459d3

This command uses an inline yaml syntax for the Data Spec. The spec consists of a single field ``demo``. The value
for the demo key is the Field Spec. The Field Spec has a type of ``uuid``, which is all that is needed for this spec.
The command tells the datacraft tool to turn off logging and to generate 5 records from this inline spec. The default
is for output to be printed to the console. Inline Data Specs can be useful for testing and development. Most Data
Specs will be in JSON or YAML files. Use the ``--debug-spec`` flag to dump the inline spec out as JSON for easier
additions and configuration changes. Use the ``--debug-spec-yaml`` flag if you prefer to work with the more compact
YAML format.

.. code-block:: text

    $ datacraft --inline "{demo: {type: uuid}}" --log-level off --debug-spec > demo.json
    $ cat demo.json
    {
        "demo": {
            "type": "uuid"
        }
    }
    $ datacraft -s demo.json --log-level off -i 5
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
        "count": {"type": "rand_int_range", "data": [1,100]}
    }

Here we define the three fields of our record: ``id``, ``timestamp``, and ``count``. The portion after the name is
called a Field Spec. This defines the type of data the field consists of and how it should be generated. The ``id``
field is a ``uuid`` just like the previous example.  The ``timestamp`` is a ISO 8601 date and the ``count`` is a random
integer between 1 and 100. If we run this spec and specify the ``--format json`` flag:

.. code-block:: shell

    $ datacraft -s demo.json --log-level off -i 5 --format json -x
    {"id": "706bf38c-02a8-4087-bf41-62cdf4963f0b", "timestamp": "2050-11-30T05:21:14", "count": 59}
    {"id": "d96bad3e-45c3-424e-9d4e-1233f9ed6ab5", "timestamp": "2050-11-09T20:21:03", "count": 61}
    {"id": "ff3b8d87-ab3d-4ebe-af35-a081ee5098b5", "timestamp": "2050-11-05T08:24:05", "count": 36}
    {"id": "b6fbd17f-286b-4d58-aede-01901ae7a1d7", "timestamp": "2050-11-10T09:37:47", "count": 16}
    {"id": "f4923efa-28c5-424a-8560-49914dd2b2ac", "timestamp": "2050-11-19T17:28:13", "count": 29}

There are other output formats available and a mechanism to register custom formatters. If a csv file is more suited
for your needs:

.. code-block:: shell

    $ datacraft -s demo.json --log-level off -i 5 --format csv -x
    1ad0b69b-0843-4c0d-90a3-d7b77574a3af,2050-11-21T21:24:44,2
    b504d688-6f02-4d41-8b05-f55a681b940a,2050-11-14T15:29:59,76
    11502944-dacb-4812-8d73-e4ba693f2c05,2050-11-24T00:17:55,98
    8370f761-66b1-488e-9327-92a7b8d795b0,2050-11-08T02:55:11,4
    ff3d9f36-6560-4f26-8627-e18dea66e26b,2050-11-15T07:33:42,89

Spec Formats
------------

A Data Spec can be created in multiple formats.  The most common is the JSON syntax described above. Another format
that is supported is YAML:

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

Here the combine type takes a refs argument that specifies the name of two or more references to combine the values of.
There is also a ``ref`` type. This is useful for making Data Specs easier to read by segmenting the structures into
smaller pieces.  This is particularly useful with ``nested`` types:

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

    $ datacraft -s refs_type.json -i 3 --log-level off --format json -x
    {"outer": {"simple_uuid": "c77a5bee-83bb-4bae-a8e8-21be735f73c9", "complex_value": "'~4.028 microns per second'"}}
    {"outer": {"simple_uuid": "5d27eb03-c5a3-4167-9dd1-56c1f0b5a49c", "complex_value": "'~21.221 microns per second'"}}
    {"outer": {"simple_uuid": "6fa92f9f-d3ac-4118-ad2f-89b73bafb7c5", "complex_value": "'~27.432 microns per second'"}}


Templating
----------

Datacraft supports templating using the `Jinja2 <https://pypi.org/project/Jinja2/>`_ templating engine format. To
populate a template file or string with the generated values for each iteration, pass the ``-t /path/to/template``
(or template string) arg to the datacraft command. The basic format for a template is to put the field names in
``{{field name }}`` notation wherever they should be substituted. For example, the following is a template for bulk
indexing data into Elasticsearch.

.. code-block:: json

   {"index": {"_index": "test", "_id": "{{ id }}"}}
   {"doc": {"name": "{{ name }}", "age": "{{ age }}", "color": "{{ color }}"}}

We could then create a spec to populate the id, name, age, and color fields. Such as:

.. code-block:: json

   {
     "id": {"type": "range", "data": [1, 10]},
     "color": {"red": 0.33, "blue": 0.44, "yellow": 0.33},
     "name": [
         "bob", "rob", "bobby", "bobo", "robert", "roberto", "bobby joe", "roby", "robi", "steve"
     ],
     "age": {"type": "range", "data": [22, 44, 2]}
   }

When we run the tool we get the data populated for the template:

.. code-block:: shell

   datacraft -s es-spec.json -t template.json -i 10 --log-level off -x
   {"index": {"_index": "test", "_id": "3"}}
   {"doc": {"name": "bobby", "age": "26", "color": "yellow"}}
   {"index": {"_index": "test", "_id": "4"}}
   {"doc": {"name": "bobo", "age": "28", "color": "blue"}}
   {"index": {"_index": "test", "_id": "5"}}
   {"doc": {"name": "robert", "age": "30", "color": "blue"}}
   {"index": {"_index": "test", "_id": "6"}}
   {"doc": {"name": "roberto", "age": "32", "color": "red"}}
   {"index": {"_index": "test", "_id": "7"}}
   ...

It is also possible to do templating inline from the command line:

.. code-block:: shell

   datacraft -s es-spec.json -i 5 --log-level off -x --template '{{name}}: ({{age}}, {{color}})'
   bob: (22, red)
   rob: (24, blue)
   bobby: (26, blue)
   bobo: (28, yellow)
   robert: (30, red)

Loops in Templates
^^^^^^^^^^^^^^^^^^

`Jinja2 Control Structures <https://jinja.palletsprojects.com/en/2.11.x/templates/#list-of-control-structures>`_
support looping. To provide multiple values to use in a loop use the ``count`` parameter. Modifying the
example from the Jinja2 documentation to work with datacraft:

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


.. _templating_specs:

Templating Specs
----------------

There may be parts of a spec that you want to be variable. You can use the jinja2 templating format to template the
parts of the spec that should be variable. For example:

.. code-block:: text

   {
     "prize": {
       "type": "values",
       "data": {
         "ball": 0.4,
         "gum": 0.3,
         "big ball": 0.1,
         "frisbee": 0.1,
         "puppy": 0.05,
         "diamond ring": 0.005,
         "tesla": 0.0005
       },
       "config": {
         "count": {{ prize_count | default(1, true) | int }}
       }
     }
   }

In this example the count for the the prize field is variable. The default is 1, but can be overridden from the
command line by specifying a ``--var-file /path/to/vars.json`` or with the ``-vars key1=value1 key2=value2`` flags.
Running the command with no vars specified:

.. code-block:: shell

   $ datacraft -s vars_test.json -i 3 --log-level warn
   ['frisbee']
   ['ball']
   ['gum']

Now with ``prize_count`` set to 3

.. code-block:: shell

   $ datacraft -s vars_test.json -i 3 --log-level warn -v prize_count=3
   ['gum', 'big ball', 'ball']
   ['puppy', 'big ball', 'gum']
   ['gum', 'ball', 'tesla']

NOTE: It is a good practice to use a default in case that a variable is not defined, or that the variable
substitution flags are not specified. With no default, the value would become blank and render the JSON invalid.

NOTE: If using a ``calculate`` spec with a ``formula`` specified, or a ``templated`` spec, these will need to be
adjusted if you are also using templated values in your spec. You will need to adjust the formula and data elements
so they are correctly interpreted by the Jinja2 templating engine. The template will need to be wrapped in a quoted
literal with the existing value in it. i.e ``"{{ field }}other stuff"`` becomes ``"{{ '{{ field }}other stuff' }}"``

.. tabs::

   .. tab:: Before

      .. code-block:: json

         {
           "sum": {
             "type": "calculate",
             "formula": "{{one}} + {{two}}",
             "refs": ["one", "two"]
           },
           "system": {
             "type": "templated",
             "data": "p{{var1}}.53.{{var2}}.01",
             "refs": ["var1", "var2"]
           },
           "refs": {
             "one": [1, 1.0, 1.0000001],
             "two": [2, 2.0, 2.0000001],
             "var1:rand_int_range": [0, 100],
             "var2:rand_int_range": [0, 100]
           }
         }

   .. tab:: After

      .. code-block:: json

         {
           "sum": {
             "type": "calculate",
             "formula": "{{ '{{one}} + {{two}}' }}",
             "refs": ["one", "two"]
           },
           "system": {
             "type": "templated",
             "data": "{{ 'p{{var1}}.53.{{var2}}.01' }}",
             "refs": ["var1", "var2"]
           },
           "refs": {
             "one": [1, 1.0, 1.0000001],
             "two": [2, 2.0, 2.0000001],
             "var1:rand_int_range": [0, 100],
             "var2:rand_int_range": [0, 100]
           }
         }

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
Below is an updated version of the spec with the ``field_groups`` specified to give the 50/50 output. This uses the
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

   $ datacraft -s pets.json -i 10 -l off -x --format json
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

Instead of hard coding large numbers of values into a Data Spec, these can be externalized using one of the
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

NOTE: If you don't want to hard code the names of the datafiles to use in the spec, you can make use of the
:ref:`Spec Templating<templating_specs>` feature described above.

.. code-block:: shell

    datacraft -s spec.json -d dir_with_csvs --log-level off -i 3
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
field, it will not be enabled, even if set on a later field. It is safest to define the sample_rows param in a
config_ref that all of the fields share, as illustrated in the above example.

Processing Large CSVs
^^^^^^^^^^^^^^^^^^^^^

There are Field Specs that support using csv data to feed the data generation process. If the input CSV file is very
large, not all features will be supported. You will not be able to set sampling to true or use a field count > 1. The
maximum number of iterations will be equal to the size of the smallest number of lines for all the large input CSV
files. The current size threshold is set to 250 MB. So, if you are using two different csv files as inputs and one is
300 MB with 5 million entries and another is 500 MB with 2 million entries, you will be limited to 2 million
iterations before an exception will be raised and processing will cease. You can override the default size limit on
the command line by using the ``--set-default`` flag. Example:

.. code-block:: shell

   datacraft --set-default large_csv_size_mb=1024 --datadir path/to/large.csv ...

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

   $ datacraft --spec csv-select.yaml -i 5 --datadir ./data --format json --log-level off -x
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
package to allow auto discovery of custom functions using decorators. Use the ``@datacraft.registry.types('<type key>')``
to register a function that will create a :ref:`Value Supplier<value_supplier_interface>` for the supplied Field
Spec. Below is an example of a custom class which reverses the output of another supplier. This same operation could
also be done with a :ref:`custom caster<custom_value_casters>`

To supply custom code to the tool use the ``-c`` or ``--code`` arguments. One or more module files can be imported.

.. tabs::

   .. tab:: Custom Code

      .. code-block:: python

         import datacraft

         class ReverseStringSupplier(datacraft.ValueSupplierInterface):
             def __init__(self, wrapped):
                 self.wrapped = wrapped

             def next(self, iteration):
                 # value from the wrapped supplier
                 value = str(self.wrapped.next(iteration))
                 # python way to reverse a string, hehe
                 return value[::-1]

         @datacraft.registry.types('reverse_string')
         def configure_supplier(field_spec: dict,
                                loader: datacraft.Loader) -> datacraft.ValueSupplierInterface:
             # load the supplier for the given ref
             key = field_spec.get('ref')
             wrapped = loader.get(key)
             # wrap this with our custom reverse string supplier
             return ReverseStringSupplier(wrapped)

         @datacraft.registry.schemas('reverse_string')
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

         .datacraft -s reverse-spec.json -i 4 -c custom.py another.py -x --log-level off
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

See the :ref:`Registry Decorators<registry_decorators>` for the complete list of components that can be expanded or
registered.

Custom Type Usage
^^^^^^^^^^^^^^^^^

There is an additional decorator that can be used to register usage help for a custom type:
``@datacraft.registry.usage(<my_custom_type>)``. Example:

.. code-block:: python

   import datacraft

   @datacraft.registry.usage('reverse_string')
   def get_reverse_string_usage():
       example = {
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
       example_str = json.dumps(example, indent=4)
       command = 'datacraft -s spec.json -i 5 --format json-pretty -x -l off'
       output = json.dumps(datacraft.entries(example, 5, enforce_schema=True), indent=4)
       return '\n'.join([
           "Reverses output of other suppliers",
           "Example:", example_str,
           "Command:", command,
           "Output:", output
       ])

.. code-block:: shell

   datacraft -c custom.py --type-help reverse_string -l off
   -------------------------------------
   reverse_string | Reverses output of other suppliers
   Example:
   {
       "backwards": {
           "type": "reverse_string",
           "ref": "ANIMALS"
       },
       "refs": {
           "ANIMALS": {
               "type": "values",
               "data": [
                   "zebra",
                   "hedgehog",
                   "llama",
                   "flamingo"
               ]
           }
       }
   }
   Command:
   datacraft -s spec.json -i 5 --format json-pretty -x -l off
   Output:
   [
       {
           "backwards": "arbez"
       },
       {
           "backwards": "gohegdeh"
       },
       {
           "backwards": "amall"
       },
       {
           "backwards": "ognimalf"
       },
       {
           "backwards": "arbez"
       }
   ]
   -------------------------------------

If you want different usage for the command line help from python, you can return a dictionary with ``api`` and ``cli``
as the keys:

.. code-block:: python

   import datacraft

   @datacraft.registry.usage('reverse_string')
   def get_reverse_string_usage():
       return {
         "api": "import datacraft\n...",
         "cli": "datacraft -c custom.py -s spec.json ..."
       }

Custom Types Entry Point
^^^^^^^^^^^^^^^^^^^^^^^^

Datacraft provides a way to discover registered types using the ``datacraft.custom_type_loader`` entry point. At load
time all the entry points for this key are loaded. This allows users to create their own libraries and packages
that use the :ref:`@datacraft.registry.*<registry_decorators>` decorators. To add an entry point to your setup.cfg or
setup.py for the `datacraft.custom_type_loader`:

.. tabs::

   .. tab:: setup.cfg

      .. code-block::

         [options.entry_points]
         datacraft.custom_type_loader =
             mycustomstuff = mypackage:load_custom

   .. tab:: setup.py

      .. code-block:: python

         from setuptools import setup

         setup(
             name='toolname',
             version='0.0.1',
             packages=['mypackage'],
             # ...
             entry_points={
                 'datacraft.custom_type_loader': ['mycustomstuff=mypackage:load_custom']
             }
         )

Then in the `mypackage` `__init__.py` you can define `load_custom`:

.. code-block:: python

   import datacraft

   class ReverseStringSupplier(datacraft.ValueSupplierInterface):
       def __init__(self, wrapped):
           self.wrapped = wrapped

       def next(self, iteration):
           # value from the wrapped supplier
           value = str(self.wrapped.next(iteration))
           # python way to reverse a string, hehe
           return value[::-1]

   def load_custom():
      @datacraft.registry.types('reverse_string')
      def configure_supplier(field_spec: dict,
                             loader: datacraft.Loader) -> datacraft.ValueSupplierInterface:
          # load the supplier for the given ref
          key = field_spec.get('ref')
          wrapped = loader.get(key)
          # wrap this with our custom reverse string supplier
          return ReverseStringSupplier(wrapped)

      @datacraft.registry.schemas('reverse_string')
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

Note that the decorated functions are not required to be defined inside the load_custom() function. If your package
is installed with pip or another package manager, your custom registered suppliers and other functions will be
automatically discovered and loaded by the datacraft tooling at run time.

Programmatic Usage
------------------

The simplest way to use datacraft programmatically is to have a spec as a dictionary that mirrors the JSON format:

.. code-block:: python

   import datacraft

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

   print(*datacraft.entries(raw_spec, 3), sep='\n')

.. code-block:: python

   {'email': 'zebra_fling@gmail.com'}
   {'email': 'hedgehog_fling@yahoo.com'}
   {'email': 'llama_dispatch@hotmail.com'}


Record Generator
^^^^^^^^^^^^^^^^

The :ref:`spec.generator<data_spec_class>` function will create a python generator that can be used to incrementally
generate the records from the DataSpec.

Example:

.. code-block:: python

    import datacraft

    raw_spec {'name': ['bob', 'bobby', 'robert', 'bobo']}
    spec = datacraft.parse_spec(raw_spec)

    template = 'Name: {{ name }}'
    # need this to apply the data to the template
    processor = datacraft.outputs.processor(template=template)

    generator = spec.generator(
       iterations=5,
       processor=processor)

    single_record = next(generator)
    # 'Name: bob'
    remaining_records = list(generator)  # five iterations wraps around to first
    # ['Name: bobby', 'Name: robert', 'Name: bobo', 'Name: bob']


Pandas DataFrame
^^^^^^^^^^^^^^^^

The DataSpec object has a convenient to_pandas() method to that will convert the specified number of iterations into
a pandas DataFrame with that many rows. **NOTE** The ``pandas`` module is not installed by default as one of the
datacraft dependencies. Please install it first with pip or conda. Example using the to_pandas() method:

.. code-block:: python

   import datacraft

   raw_spec = {
     "http_code": {
       "type": "weighted_ref",
       "data": {"GOOD_CODES": 0.7, "BAD_CODES": 0.3}
     },
     "end_point": [ "/data", "/payment", "/login", "/users" ],
     "refs": {
       "GOOD_CODES": {
         "200": 0.5,
         "202": 0.3,
         "203": 0.1,
         "300": 0.1
       },
       "BAD_CODES": {
         "400": 0.5,
         "403": 0.3,
         "404": 0.1,
         "500": 0.1
       }
     }
   }

   spec = datacraft.parse_spec(raw_spec)

   # print single generated record
   df = spec.to_pandas(10)

   print(df.head())
   #   http_code end_point
   # 0       200     /data
   # 1       203  /payment
   # 2       400    /login
   # 3       200    /users
   # 4       202     /data
   gb = df.groupby('http_code')[['end_point']].agg(set)

   print(gb.head())
   #                          end_point
   # http_code
   # 200                {/data, /users}
   # 202        {/users, /data, /login}
   # 203                     {/payment}
   # 400             {/payment, /login}
   # 500                     {/payment}

REST Server
-----------

Datacraft comes with a lightweight Flask server to use to retrieve generated data. Use the ``--server`` with the
optional ``--server-endpoint /someendpoint`` flags to launch this server.  The default end point will be found at
http://127.0.0.1:5000/data. If using a template, each call to the endpoint will return the results of applying a
single record to the template data. If you specify one of the ``--format`` flags, the formatted record will be returned
as a string. If neither a formatter or a template are applied, the record for each iteration will be returned as JSON.
Note that using the ``--records-per-file`` with a number greater than one and a --format of json or json-pretty, will
produce escaped JSON, which is probably not what you want.

Example
^^^^^^^

For this example we use the inline yaml spec: ``{id:uuid: {}, ts:date.iso: {}}`` as the data we want returned from our
endpoint. The command below will spin up a flask server that will format the record using the json-pretty formatter.
The records contain a uuid and a timestamp field.

.. code-block:: shell

    $ datacraft --inline "{id:uuid: {}, ts:date.iso: {}}" -i 2 --log-level debug --format json-pretty --server
     * Serving Flask app 'datacraft.server' (lazy loading)
     * Environment: production
       WARNING: This is a development server. Do not use it in a production deployment.
       Use a production WSGI server instead.
     * Debug mode: off
     * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
    127.0.0.1 - - [23/Nov/2050 20:48:41] "GET /data HTTP/1.1" 200 -
    127.0.0.1 - - [23/Nov/2050 20:48:44] "GET /data HTTP/1.1" 200 -
    No more iterations available
    127.0.0.1 - - [23/Nov/2050 20:48:46] "GET /data HTTP/1.1" 204 -

Here is the client side of the transaction, where we perform a GET request on the /data endpoint.

.. code-block:: bash

    $ curl -s -w "\n%{http_code}\n%" http://127.0.0.1:5000/data
    {
        "id": "b614698e-1429-4ff7-ac6a-223b26e18b31",
        "ts": "2050-04-25T08:11:41"
    }
    200
    $ curl -s -w "\n%{http_code}\n%" http://127.0.0.1:5000/data
    {
       "id": "116a0531-0062-42bc-9224-27774851022b",
       "ts": "2050-04-27T16:53:04"
    }
    200
    $ curl -s -w "\n%{http_code}\n%" http://127.0.0.1:5000/data

    204

In this exchange, three requests are made.  The first two return the generated data formatted. The third returns a 204
or No Content response code.  This is because the number of iterations was set to 2.
