.. _spec_inference:

Data Spec Inference
====================

The new `infer-spec` utility in the Datacraft toolkit allows you to automatically infer a Data Spec from provided sample
data in either CSV or JSON format. Instead of manually crafting your data specification, you can now use this handy
utility to get a head start from your sample datasets.

Command Line Usage
------------------

To infer a Data Spec, use the following command:

.. code-block:: bash

   infer-spec (--csv <CSV_PATH> | --json <JSON_PATH> | --csv-dir <CSV_DIRECTORY_PATH> | --json-dir <JSON_DIRECTORY_PATH>) [OPTIONS]

Options:
^^^^^^^^

-h, --help
   Show this help message and exit.

--csv CSV
   Path to a single CSV file to process.

--json JSON
   Path to a single JSON file to process.

--csv-dir CSV_DIR
   Directory path containing multiple CSV files for batch processing.

--json-dir JSON_DIR
   Directory path containing multiple JSON files for batch processing.

--csv-select CSV_SELECT
   Path to CSV file, infers a csv-select spec from file

--output OUTPUT
   Specifies the output file to write the inferred Data Spec results.

--limit LIMIT
   Set the max size for lists or weighted values, particularly useful when a specific type from the data cannot be inferred.

--limit-weighted
   For weighted values, this option ensures only the top `limit` weights are considered in the inferred spec.

-l, --log-level {critical,fatal,error,warning,warn,info,debug,off,stop,disable}
   Set the verbosity of the logging. The default level is `info`.

Example Workflow
----------------

Suppose you have a sample data file named `sample.csv` and you want to infer its Data Spec.
Here's how you might use the `infer-spec` tool:

.. code-block:: bash

   infer-spec --csv sample.csv --output inferred_spec.json

This would process the `sample.csv` file, infer the Data Spec, and then save the result to `inferred_spec.json`. For
the example csv below:

.. code-block:: none

   ip,lat,long,city,date
   192.168.1.1,34.0522,-118.2437,Los Angeles,2023-10-08T08:45:00
   192.168.1.2,40.7306,-73.9352,New York,2023-10-08T09:15:23
   192.168.1.3,51.5074,-0.1278,London,2023-10-08T10:32:50
   192.168.1.4,48.8566,2.3522,Paris,2023-10-08T11:05:31
   192.168.1.5,35.6895,139.6917,Tokyo,2023-10-08T12:22:14
   192.168.1.6,37.7749,-122.4194,San Francisco,2023-10-08T13:35:22
   192.168.1.7,41.8781,-87.6298,Chicago,2023-10-08T14:45:50
   192.168.1.8,34.0522,-118.2437,Los Angeles,2023-10-08T15:55:33
   192.168.1.9,49.2827,-123.1207,Vancouver,2023-10-08T16:30:05
   192.168.1.10,52.5200,13.4050,Berlin,2023-10-08T17:10:14
   192.168.1.11,28.6139,77.2090,New Delhi,2023-10-08T18:02:21


Running this through `infer-spec` tool will produce the following Data Spec:

.. code-block:: json

    {
      "ip": {
        "type": "ip",
        "config": {
          "base": "192.168.1"
        }
      },
      "lat": {
        "type": "geo.lat"
      },
      "long": {
        "type": "geo.long"
      },
      "city": {
        "type": "values",
        "data": [
          "New York",
          "New Delhi",
          "Paris",
          "Los Angeles",
          "Berlin",
          "London",
          "Tokyo",
          "Chicago",
          "Vancouver"
        ]
      },
      "date": {
        "type": "date.iso"
      }
    }

Keep in mind that while the generated data will resemble the source CSV, it won't retain the original's correlations.

CSV Select
----------

The :ref:`csv_select` type can be used to simplify including externalized data into a Data Spec. To simplify the
creation of these types of specs, you can use the ``--csv-select /path/to/file.csv`` command line option. For example
if you had a csv like:

.. code-block:: text

    player_id,name,level,event_id,event_type
    1001,Alice,10,E101,Quest
    1002,Bob,12,E102,Battle
    1003,Charlie,8,E103,Trade
    1004,Diana,15,E104,Exploration
    1005,Ethan,9,E105,Duel
    1006,Fiona,11,E106,Tournament
    1007,George,14,E107,Quest
    1008,Hannah,7,E108,Battle
    1009,Ian,13,E109,Trade

Running the ``infer-spec`` cli tool with the ``--csv-select`` against this csv would result in a Data Spec like this:

.. code-block:: shell

    $ infer-spec.exe --csv-select game.csv
    {
        "placeholder": {
            "type": "csv_select",
            "data": {
                "player_id": 1,
                "name": 2,
                "level": 3,
                "event_id": 4,
                "event_type": 5
            },
            "config": {
                "datafile": "game.csv",
                "headers": true
            }
        }
    }

Note that if the CSV file does not include headers, the names of the fields will be the first value in each field:

.. code-block:: shell

    $ infer-spec.exe --csv-select game-no-headers.csv
    {
        "placeholder": {
            "type": "csv_select",
            "data": {
                "1001": 1,
                "Alice": 2,
                "10": 3,
                "E101": 4,
                "Quest": 5
            },
            "config": {
                "datafile": "game-no-headers.csv",
                "headers": true
            }
        }
    }

API Usage
---------

The `datacraft.infer` module provides a function `from_examples` that can generate a Data Spec from a list
of example JSON records. This is particularly useful if you have a sample of data and wish to automatically create
a Data Spec based on the patterns and structures observed in that data.

Basic Usage
^^^^^^^^^^^

To use the `from_examples` function, provide it with a list of dictionaries representing your sample data:

.. code-block:: python

    import json

    import datacraft.infer as infer

    examples = [
        {
            "order": {
                "drink": "cortado",
                "shots": 1,
                "milk": "whole",
                "size": "small"
            }
        },
        {
            "order": {
                "drink": "cappuccino",
                "shots": 2,
                "milk": "oat",
                "size": "medium",
            }
        },
        {
            "order": {
                "drink": "latte",
                "shots": 3,
                "milk": "almond",
                "size": "large"
            }
        }
    ]

    spec = infer.from_examples(examples)
    print(json.dumps(spec, indent=2))

This will output:

.. code-block:: json

    {
      "order": {
        "type": "nested",
        "fields": {
          "drink": {
            "type": "values",
            "data": ["cappuccino", "latte", "cortado"]
          },
          "shots": {
            "type": "rand_int_range",
            "data": [1, 2]
          },
          "milk": {
            "type": "values",
            "data": ["whole", "almond", "oat"]
          },
          "size": {
            "type": "values",
            "data": ["small", "medium", "large"]
          }
        }
      }
    }

We can now use the generated spec to produce test data:

.. code-block:: python

    import datacraft

    print(*datacraft.entries(spec, 3), sep='\n')
    #{'order': {'drink': 'latte', 'shots': 2, 'milk': 'almond', 'size': 'small'}}
    #{'order': {'drink': 'cappuccino', 'shots': 2, 'milk': 'oat', 'size': 'large'}}
    #{'order': {'drink': 'cortado', 'shots': 1, 'milk': 'whole', 'size': 'medium'}}

Advanced Options
^^^^^^^^^^^^^^^^

The `from_examples` function supports some keyword arguments to fine-tune the spec inference:

- `limit`: If a spec will produce a list of values, this will be the max size of the list. It will be sampled to fit this size.
- `limit_weighted`: Some analyzers will produce weighted values. These can also be large. If `limit_weighted` is set to True, then the top limit size weighted values will be retained.
- `duplication_threshold`: ratio of unique to total items, if above this threshold, use weighted values

Examples:

.. code-block:: python

    import datacraft.infer as infer

    # four records that contain four different values for the key "one"
    examples = [
        {"one": "a"},
        {"one": "b"},
        {"one": "c"},
        {"one": "d"},
    ]
    # sample 3 of the values for our spec
    print(infer.from_examples(examples, limit=3))
    {'one': {'type': 'values', 'data': ['d', 'b', 'c']}}

    # the value 'a' appears frequently in these records
    # by default if the ratio of unique to total records is > 0.5, we use a weighted value scheme
    examples = [
        {"one": "a"},
        {"one": "a"},
        {"one": "a"},
        {"one": "b"},
        {"one": "c"},
        {"one": "d"},
    ]
    # by default, if the weight values threshold is triggered, we don't limit it
    print(infer.from_examples(examples, limit=3))
    {'one': {'type': 'values', 'data': {'a': 0.5, 'b': 0.16667, 'c': 0.16667, 'd': 0.16667}}}

    # to limit weighted values, set the limit_weighted parameter to True
    print(infer.from_examples(examples, limit=3, limit_weighted=True))
    # here we take the top three weighted values
    {'one': {'type': 'values', 'data': {'a': 0.5, 'b': 0.16667, 'c': 0.16667}}}

    print(infer.from_examples(examples, duplication_threshold=0.51))
    # here we set the duplication threshold to over 50% and the values are retained as is
    {'one': {'type': 'values', 'data': ['a', 'a', 'a', 'b', 'c', 'd']}}

Notes
-----

This utility is designed to give you a starting point. Depending on the complexity and nuances of your sample data,
you might still need to tweak or refine the inferred spec to suit your specific requirements.

Not all data is easily mapped to one of the basic field spec types. If there are a lot of unique strings in your data
set, you may want to make use of the ``--limit N`` flag. This will take a sample of the values if the number of unique
values exceeds this limit.

For the best results, it is helpful to have uniformly structured data for a specific Entity type. For example,
having a directory with both customer profiles and product listings can lead to ambiguities or inaccuracies when
inferring a Data Spec, as the fields and data types for each entity can vary significantly. This is especially true
if there are field names that are the same but have different underlying data values.

It is also helpful to have multiple examples of a record. A good practice is to have at least one example with minimum
values and one with maximum. You infer a spec from a single example, but it might not be as helpful. In this way a csv
file with example values might be easier to start with.

There are some edge case structures that the tool is not set up to support at this time such as deeply nested
lists:

.. code-block:: python

    examples = [
        {
            "crazy_list": [
                [
                    ["way", "down", "deep"]
                ]
            ]
        }

    ]
    print(infer.from_examples(examples))
    # this will just reproduce the example list over and over
    {'crazy_list': {'type': 'values', 'data': [[[['way', 'down', 'deep']]]]}}
