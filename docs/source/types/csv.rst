csv types
---------

If you have an existing large set of data in a tabular format that you want to
use, it would be burdensome to copy and paste the data into a spec. To make use
of data already in a tabular format you can use a ``csv`` Field Spec. These specs
allow you to identify a column from a tabular data file to use to provide the
values for a field. Another advantage of using a csv spec is that it is easy to
have fields that are correlated be generated together. All rows will be selected
incrementally, unless any of the fields are configured to use ``sample`` mode. You
can use ``sample`` mode on individual columns, or you can use it across all
columns by creating a ``config_ref`` spec. See ``csv_select`` for an
efficient way to select multiple columns from a csv file.

csv
^^^

Prototype:

.. code-block:: python

    {
      "<field name>": {
        "type": "csv",
        "config": {
          "datafile": "filename in datedir",
          "headers": "yes, on, true for affirmative",
          "column": "1 based column number or field name if headers are present",
          "delimiter": "how values are separated, default is comma",
          "quotechar": "how values are quoted, default is double quote",
          "sample": "If the values should be selected at random, default is false",
          "count": "Number of values in column to use for value"
        }
      }
    }

Examples:

.. code-block:: json

    {
      "cities": {
        "type": "csv",
        "config": {
          "datafile": "cities.csv",
          "delimiter": "~",
          "sample": true
        }
      }
    }

.. code-block:: json

    {
      "status": {
        "type": "csv",
        "config": {
          "column": 1,
          "config_ref": "tabs_config"
        }
      },
      "description": {
        "type": "csv",
        "config": {
          "column": 2,
          "config_ref": "tabs_config"
        }
      },
      "status_type:csv?config_ref=tabs_config&column=3": {},
      "refs": {
        "tabs_config": {
          "type": "config_ref",
          "config": {
            "datafile": "tabs.csv",
            "delimiter": "\\t",
            "headers": true,
            "sample_rows": true
          }
        }
      }
    }

.. _csv_select:

csv_select
^^^^^^^^^^

Prototype:

.. code-block:: python

    {
      "<field name>": {
        "type": "csv_select",
        "data": {
          "<field_one>": <1 based column index for field 1>,
          "<field_two>:<cast>": <1 based column index for field 2>,
          "<field_tre>": {
            "col": <1 based column index for field 3>,
            "cast": "<valid cast value i.e. int, float, etc"
          },
          ...,
          "<field n>":
          }
        },
        "config": {
          "datafile": "filename in datedir, or templated name i.e. {{ to_be_filled }}",
          "headers": "yes, on, true for affirmative",
          "delimiter": "how values are separated, default is comma",
          "quotechar": "how values are quoted, default is double quote"
        }
      }
    }

Examples:

.. code-block:: json

    {
      "placeholder": {
        "type": "csv_select",
        "data": {
          "geonameid": 1,
          "name": 2,
          "latitude:float": 5,
          "longitude": { "col": 6, "cast": "float" },
          "country_code": 9,
          "population:int": 15
        },
        "config": {
          "datafile": "allCountries.txt",
          "headers": false,
          "delimiter": "\t"
        }
      }
    }

In the example above, the latitude and longitude columns are both cast to floating point numbers and the population
is cast to an integer. See :ref:`casters` for details on available casting types.

weighted_csv
^^^^^^^^^^^^

This is useful when you have a large number of weighted values that would not fit nicely into a JSON file. You can
specify a value and a weight for that value. The default is that the first column in the csv is the value and the
second column is the weight.  Example CSV:

.. code-block::

    city,weight
    New York,0.65
    Los Angeles,0.23
    London,0.87
    Paris,0.49
    Tokyo,0.32
    Sydney,0.91
    Beijing,0.04
    Rio de Janeiro,0.78
    Mumbai,0.56
    Cape Town,0.38

Prototype:

.. code-block:: python

    {
      "<field name>": {
        "type": "weighted_csv",
        "config": {
          "datafile": "filename in datedir",
          "headers": "yes, on, true for affirmative",
          "column": "1 based column number or field name if headers are present",
          "weight_column": "1 based column number or field name if headers are present where weights are defined"
          "delimiter": "how values are separated, default is comma",
          "quotechar": "how values are quoted, default is double quote",
          "sample": "If the values should be selected at random, default is false",
          "count": "Number of values in column to use for value"
        }
      }
    }

Examples:

.. code-block:: json

    {
      "cities": {
        "type": "weighted_csv",
        "config": {
          "datafile": "weighted_cities.csv"
        }
      }
    }