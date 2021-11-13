Command Line Interface
======================

There are several options when using ``datagen`` from the command line.

Inline JSON/YAML
----------------

To test small spec fragments, you can use the ``--inline <spec>`` flag. Example:

.. code-block:: shell

   datagen --inline '{ "handle": { "type": "cc-word", "config": {"min": 3, "mean": 5, "prefix": "@" } } }' \
     --iterations 5 \
     --printkey \
     --log-level off
   handle -> @r3Wl
   handle -> @cCyfSeU
   handle -> @l8n
   handle -> @aUb
   handle -> @jf7Ax

Log Levels
----------

You can change the logging levels to one of ``debug, info, warn, error, or off`` by using the ``-l`` or
``--log-level`` flag. See example above.

Formatting Output
-----------------

Sometimes it may be useful to dump the generated data into a format that is easier to consume or view. Use the ``-f``
or ``--format`` flag to specify one of ``json`` or ``json-pretty`` or ``csv``. The ``json`` format will print a flat
version of each record that takes up a single line for each iteration. The ``json-pretty`` format will print an
indented version of each record that will span multiple lines. The ``csv`` format will output each record as a comma
separated value line. Examples:

.. code-block:: shell

   # NOTE: This inline spec is in YAML
   datagen --inline 'handle: { type: cc-word, config: {min: 3, mean: 5, prefix: "@" } }' \
       --iterations 2 \
       --log-level off \
       --format json \
       --exclude-internal
   {"handle": "@a2oNt"}
   {"handle": "@lLN3i"}

   datagen --inline 'handle: { type: cc-word, config: {min: 3, mean: 5, prefix: "@" } }' \
       --iterations 2 \
       --log-level off \
       --format json-pretty \
       --exclude-internal
   {
       "handle": "@ZJeE_f"
   }
   {
       "handle": "@XmJ"
   }
   datagen --inline '{"id:uuid": {}, "handle": { "type": "cc-word", "config": {"min": 3, "mean": 5, "prefix": "@" } }' \
   41adb77f-d7b3-4a31-a75b-5faff33d5eb8,@U0gI
   d97e8dad-8dfd-49f1-b25e-eaaf2d6953fd,@IYn

Apply Raw ``--apply-raw``
-------------------------

The ``--apply-raw`` command line flag will treat the argument of the ``-s`` flag as the raw-data that should be
applied to the template. This can be helpful when working on adjusting the template that is being generated. You can
dump the generated data from N iterations using the ``--format json`` or ``--format json-pretty`` then use this as
raw input to the template file.

Debugging Specifications
------------------------

There are a bunch of shorthand formats for creating specifications. These ultimately get turned into a full spec
format. It may be useful to see what the full spec looks like after all the transformations have taken place. Use the
``--debug-spec`` to dump the internal form of the specification for inspection.

.. code-block:: shell

   datagen --inline 'geo:geo.pair?start_lat=-99.0: {}' \
     --log-level off \
     --debug-spec
   {
       "geo": {
           "config": {
               "start_lat": "-99.0"
           },
           "type": "geo.pair"
       }
   }

Schema Level Validation
-----------------------

Most of the default supported field spec types have JSON based schemas defined for them. Schema based validation is
turned off by default. Use the ``--strict`` command line flag to turn on the strict schema based checks for types
that have schemas defined. Example:

.. code-block:: shell

   datagen --inline 'geo: {type: geo.pair, config: {start_lat: -99.0}}' \
       --iterations 2 \
       --log-level info \
       --format json \
       --strict
   INFO [12-Mar-2050 07:24:11 PM] Starting Loading Configurations...
   INFO [12-Mar-2050 07:24:11 PM] Starting Processing...
   WARNING [12-Mar-2050 07:24:11 PM] -99.0 is less than the minimum of -90
   ERROR [12-Mar-2050 07:24:11 PM] Failed to validate spec type: geo.pair with spec: {'type': 'geo.pair', 'config': {'start_lat': -99.0}}

Default Values
--------------

There are some default values used when a given spec does not provide them. These defaults can be viewed using the
``--debug-defaults`` flag.

.. code-block:: shell

   datagen --debug-defaults -l off
   {
       "sample_mode": false,
       "combine_join_with": "",
       "char_class_join_with": "",
       "geo_as_list": false,
       "combine_as_list": false,
       "geo_lat_first": false,
       "geo_join_with": ",",
       "date_stddev_days": 15,
       "date_format": "%d-%m-%Y",
       "geo_precision": 4,
       "json_indent": 4
   }

The general convention is to use the type as a prefix for the key that it effects. You can save this information to
disk by specifying the ``-o`` or ``--outdir`` flag. In the output above the default ``join_with`` config param is
a comma for the ``geo`` type, but is an empty string for the ``combine`` and ``char_class`` types.

Override Defaults
-----------------

To override the default values, use the ``--defaults``
/path/to/custom_defaults.json or specify individual overrides
with ``--set-defaults key=value``.

.. code-block:: shell

   datagen --debug-defaults -l off --defaults /path/to/custom_defaults.json
   {
       "sample_mode": true,
       "combine_join_with": ";",
       "char_class_join_with": "-",
       "geo_as_list": true,
       "combine_as_list": false,
       "geo_lat_first": false,
       "geo_join_with": ",",
       "date_stddev_days": 42,
       "date_format": "%Y-%m-%d",
       "geo_precision": 5,
       "json_indent": 2,
       "custom_thing": "foo"
   }

   datagen --debug-defaults -l off --set-defaults date_format="%Y_%m_%d" sample_mode="true"
   {
       "sample_mode": "true",
       "combine_join_with": "",
       "char_class_join_with": "",
       "geo_as_list": false,
       "combine_as_list": false,
       "geo_lat_first": false,
       "geo_join_with": ",",
       "date_stddev_days": 15,
       "date_format": "%Y_%m_%d",
       "geo_precision": 4,
       "json_indent": 4,
       "large_csv_size_mb": 250
   }
