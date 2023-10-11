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

The `from_examples` function supports some keyword arguments to fine-tune the inference:

- `limit`: If a spec will produce a list of values, this will be the max size of the list. It will be sampled to fit this size.
- `limit_weighted`: Some analyzers will produce weighted values. These can also be large. If `limit_weighted` is set to True, then the top limit size weighted values will be retained.

For example:

.. code-block:: python

    spec = infer.from_examples(examples, limit=10, limit_weighted=True)

Refer to the :ref:`function's docstring<spec_inference_module>` for a detailed breakdown and more examples.


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
