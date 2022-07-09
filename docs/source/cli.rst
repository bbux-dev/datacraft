Command Line Interface
======================

There are several options when using ``datacraft`` from the command line.

Inline JSON/YAML
----------------

To test small spec fragments, you can use the ``--inline <spec>`` flag. Most of the examples are inline YAML,
since these work on both linux and windows based command prompts. Inline JSON is also supported. Example:

.. code-block:: shell

    datacraft --inline "{ handle: { type: cc-word, config: {min: 3, mean: 5 } } }" -i 5 --log-level off --printkey

.. code-block:: shell

    handle -> wzS
    handle -> 9LRO
    handle -> aeWMH
    handle -> enXw_u
    handle -> nTI

Log Levels
----------

You can change the logging levels to one of
``'critical', 'fatal', 'error', 'warning', 'warn', 'info', 'debug', 'off', 'stop', 'disable'`` by using the ``-l`` or
``--log-level`` flag. See example above.

Registry Help
-------------

Many of the Field Spec types, formatters, and casters are stored in the datacraft
:ref:`Registry<registry_decorators>`. Use the commands below to list and print out help for the various registered
entities.

List Types
^^^^^^^^^^

To see a list of the registered types that can be used in specs use the ``--type-list`` command line flag:

.. code-block:: shell

    datacraft --type-list

.. code-block::

   INFO [22-May-2050 06:20:02 AM] Starting Loading Configurations...
   INFO [22-May-2050 06:20:02 AM] Loading custom type loader: core
   INFO [22-May-2050 06:20:02 AM] Loading custom type loader: xeger
   calculate
   char_class
   cc-ascii
   cc-lower
   cc-upper
   ...
   uuid
   values
   xeger

Type Usage
^^^^^^^^^^

To get detailed usage for all of the types use the ``--type-help`` flag. The flag with no arguments will list all of
the available usage for all registered types. You can limit the usage printed to specific types by providing them as
args to the ``--type-help`` flag:

.. code-block:: shell

   # lists all usage
   datacraft --type-help
   # only lists help for calculate type
   datacraft --type-help calculate -l warn

.. code-block::

   -------------------------------------
   calculate | Example Spec:
   {
     "height_in": {
       "type": "values",
       "data": [60, 70, 80, 90]
     },
     "height_cm": {
       "type": "calculate",
       "fields": [
         "height_in"
       ],
       "formula": "{{ height_in }} * 2.54"
     }
   }
   datacraft -s spec.json -i 3 --format json -x -l off
   [{"height_in": 60, "height_cm": 152.4}, {"height_in": 70, "height_cm": 177.8}, {"height_in": 80, "height_cm": 203.2}]

   -------------------------------------

Specify the ``-o <directory>`` option to create a file type-help.txt, with the full usage info:

.. code-block::

   datacraft --type-help -o .
   INFO [22-May-2050 01:13:15 PM] Starting Loading Configurations...
   INFO [22-May-2050 01:13:15 PM] Loading custom type loader: core
   INFO [22-May-2050 01:13:15 PM] Loading custom type loader: xeger
   INFO [22-May-2050 01:13:15 PM] Wrote data to .\type-help.txt

Caster List
^^^^^^^^^^^

The different casting operators available can be listed with the ``--cast-list`` command line flag. The ones that
look like ``string -> str -> s`` indicate the aliases that can be used in place of the full caster name. For example:


.. code-block:: json

   {
       "age1": {
           "type": "rand_range",
           "data": [1, 100],
           "config": {
               "cast": "int"
           }
       },
       "age2:rand_range?cast=i": [1, 100],
       "age3:rand_range?cast=round3;str;f": [1, 100]
   }

.. code-block:: shell

   datacraft -s cast.json -i 1 -x -l off --format json-pretty
   [
       {
           "age1": 44,
           "age2": 74,
           "age3": 78.535
       }
   ]

The age1 and age2 fields both cast the value to an integer.  The age3 field illustrates the use of multiple casters.
This one first rounds the value to three digits then casts to a string followed by a floating point number.


Formatter List
^^^^^^^^^^^^^^

Use the command line ``--format-list`` flag to print out the list of registered formatters.

.. code-block:: shell

    datacraft --format-list -l warn

.. code-block::

   json
   json-pretty
   csv
   csvh
   csv-with-header
   yaml

Formatting Output
-----------------

The default is to write the generated values out to the console. Use the ``--printkey`` flag to print the key with
the value:

.. code-block:: shell

    datacraft --inline "{ id:uuid, ts:date }" -i 2 --log-level off

.. code-block:: shell

    6f1fad06-9eaa-4eb1-b6c4-e842682ce7d2
    28-11-2050
    493fff93-34e6-437f-bd82-71b1dee7219d
    27-11-2050

.. code-block:: shell

    datacraft --inline "{ id:uuid, ts:date }" -i 2 --log-level off --printkey

.. code-block:: shell

    id -> 9275840a-bb1e-4ec6-ae88-702d7a1906c9
    ts -> 14-11-2050
    id -> 899f8928-b5f3-4c8e-9443-5ba5f41f81a9
    ts -> 11-12-2050


Sometimes it may be useful to dump the generated data into a format that is easier to consume or view. Use the ``-f``
or ``--format`` flag to specify one of ``json`` or ``json-pretty`` or ``csv``. The ``json`` format will print a flat
version of each record that takes up a single line for each iteration. The ``json-pretty`` format will print an
indented version of each record that will span multiple lines. The ``csv`` format will output each record as a comma
separated value line. If you want headers with the csv use the ``csv-with-header`` or ``csvh`` format. Examples:

.. code-block:: shell

    datacraft --inline "{ id:uuid, ts:date }" -i 2 --log-level off --format json -x

.. code-block:: shell

    [{"id": "732376df-9adc-413e-8493-73555fae51f9", "ts": "21-04-2050"}, {"id": "d826774a-1eeb-4e35-8253-0b00a514c0d1", "ts": "02-04-2050"}]

.. code-block:: shell

    datacraft --inline "{ id:uuid, ts:date }" -i 2 --log-level off --format json-pretty -x

.. code-block:: shell

   [
       {
           "id": "4a75d0fc-46b7-4c9b-82f1-c87dcee13674",
           "ts": "09-04-2050"
       },
       {
           "id": "62db293b-d8f8-4c9a-8653-6dba8713bab9",
           "ts": "13-04-2050"
       }
   ]

.. code-block:: shell

    datacraft --inline "{ id:uuid, ts:date }" -i 2 --log-level off --format csv -x

.. code-block:: shell

    f8b87f46-ebda-4364-a042-21e6ac117762,09-12-2050
    3b0c236c-3882-4242-9f3b-053ab3da4be8,12-12-2050

.. code-block:: shell

   datacraft --inline "{ id:uuid, ts:date.iso.us }" -i 2 --log-level off --format csvh -x

.. code-block:: shell

   id,ts
   1d79ebca-9cc4-4de2-8af3-0cfc1bbd7c55,2022-07-23T19:12:41.683306
   a41e1f3a-3954-406b-b022-fc54f43f6aab,2022-07-25T10:23:19.766581

Records Per File
----------------

When writing results to a file, the default behavior is to write all records to a single file. You can modify this
by specifying the ``-r`` or ``--records-per-file`` command line argument. The behavior is different when hosting the
generated data with the ``--server`` option. In this case the default is to return a single record at a time. Use the
same ``--records-per-file`` command line argument to return more that one record per request.

Examples:

.. code-block:: shell

   datacraft --inline "{timestamp:date: {}}" -i 4 -r 2 --log-level off --format json -x
   [{"timestamp": "25-04-2050"}, {"timestamp": "06-04-2050"}]
   [{"timestamp": "09-04-2050"}, {"timestamp": "09-04-2050"}]


.. code-block:: shell

   datacraft --inline "{timestamp:date: {}}" -i 4  --log-level off --format json -x
   [{"timestamp": "22-04-2050"}, {"timestamp": "03-04-2050"}, {"timestamp": "10-04-2050"}, {"timestamp": "06-04-2050"}]


Apply Raw
---------

The ``--apply-raw`` command line flag will treat the argument of the ``-s`` flag as the raw-data that should be
applied to the template. This can be helpful when working on adjusting the template that is being generated. You can
dump the generated data from N iterations using the ``--format json`` or ``--format json-pretty`` then use this as
raw input to the template file.

Debugging Specifications
------------------------

There are a bunch of shorthand formats for creating specifications. These ultimately get turned into a full spec
format. It may be useful to see what the full spec looks like after all the transformations have taken place. Use the
``--debug-spec`` to dump the internal form of the specification for inspection. Use the ``--debug-spec-yaml`` to
dump the spec as YAML.

.. code-block:: shell

    datacraft --inline "geo:geo.pair?start_lat=-99.0: {}" --log-level off --debug-spec

.. code-block:: shell

    {
       "geo": {
           "config": {
               "start_lat": "-99.0"
           },
           "type": "geo.pair"
       }
    }

.. code-block:: shell

    datacraft --inline "geo:geo.pair?start_lat=-99.0: {}" --log-level off --debug-spec-yaml

.. code-block:: shell

    geo:
      type: geo.pair
      config:
        start_lat: '-99.0'

Schema Level Validation
-----------------------

Most of the default supported field spec types have JSON based schemas defined for them. Schema based validation is
turned off by default. Use the ``--strict`` command line flag to turn on the strict schema based checks for types
that have schemas defined. Examples:

.. code-block:: shell

    datacraft --inline "geo:geo.pair?start_lat=-99.0: {}" --log-level info -i 2 --format json --strict

.. code-block:: shell

    INFO [13-Nov-2050 02:59:25 PM] Starting Loading Configurations...
    INFO [13-Nov-2050 02:59:25 PM] Starting Processing...
    WARNING [13-Nov-2050 02:59:25 PM] '-99.0' is not of type 'number'
    ERROR [13-Nov-2050 02:59:25 PM] Failed to validate spec type: geo.pair with spec: {'config': {'start_lat': '-99.0'}, 'type': 'geo.pair'}

.. code-block:: shell

    datacraft --inline "{geo:geo.pair: {config: {start_lat: -99.0}}}" --log-level info -i 2 --format json --strict

.. code-block:: shell

    INFO [13-Nov-2050 03:00:57 PM] Starting Loading Configurations...
    INFO [13-Nov-2050 03:00:57 PM] Starting Processing...
    WARNING [13-Nov-2050 03:00:57 PM] -99.0 is less than the minimum of -90
    ERROR [13-Nov-2050 03:00:57 PM] Failed to validate spec type: geo.pair with spec: {'config': {'start_lat': -99.0}, 'type': 'geo.pair'}

.. code-block:: shell

    datacraft --inline "demo:unicode_range: {}" -i 3 --strict

.. code-block:: shell

    INFO [13-Nov-2050 03:07:36 PM] Starting Loading Configurations...
    INFO [13-Nov-2050 03:07:36 PM] Starting Processing...
    WARNING [13-Nov-2050 03:07:36 PM] 'data' is a required property

Default Values
--------------

There are some default values used when a given spec does not provide them. These defaults can be viewed using the
``--debug-defaults`` flag.

.. code-block:: shell

    datacraft --debug-defaults -l off

.. code-block:: shell

    {
        "sample_mode": false,
        "combine_join_with": "",
        "char_class_join_with": "",
        "geo_as_list": false,
        ...
        "json_indent": 4,
        "large_csv_size_mb": 250,
        "data_dir": "./data",
        "csv_file": "data.csv",
        "mac_addr_separator": ":"
    }

The general convention is to use the type as a prefix for the key that it effects. You can save this information to
disk by specifying the ``-o`` or ``--outdir`` flag. In the output above the default ``join_with`` config param is
a comma for the ``geo`` type, but is an empty string for the ``combine`` and ``char_class`` types.

Override Defaults
-----------------

To override the default values, use the ``--defaults`` /path/to/custom_defaults.json or specify individual overrides
with ``--set-defaults key=value``.

.. code-block:: shell

    datacraft --debug-defaults -l off --defaults /path/to/custom_defaults.json

.. code-block:: shell

    {
        "sample_mode": "true",
        "combine_join_with": "",
        "char_class_join_with": "",
        ...
        "large_csv_size_mb": 250,
        "data_dir": "./data",
        "csv_file": "data.csv",
        "mac_addr_separator": ":"
    }

.. code-block:: shell

    datacraft --debug-defaults -l off --set-defaults date_format="%Y_%m_%d" sample_mode="true"

.. code-block:: shell

    {
        "sample_mode": "true",
        "combine_join_with": "",
        "char_class_join_with": "",
        "geo_as_list": false,
        ...
        "date_format": "%Y_%m_%d",
        "geo_precision": 4,
        "csv_file": "data.csv",
        "mac_addr_separator": ":"
    }
