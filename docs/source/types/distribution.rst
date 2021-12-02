distribution
------------

A distribution spec can be built from one of the registered distribution types. Below is the table of the built in ones.
Custom distributions can be registered using :ref:`Custom Code<custom_code>` Loading. See :ref:`Custom Count
Distributions<custom_count_dist>` for an example.

.. table::
   :widths: 15 15 15 60

   +--------------+--------------------+---------------+--------------------------------------+
   | distribution | required arguments | optional args | examples                             |
   +==============+====================+===============+======================================+
   | uniform      | start,end          |               | "uniform(start=10, end=30)"          |
   +--------------+--------------------+---------------+--------------------------------------+
   |              |                    |               | "uniform(start=1, end=3)"            |
   +--------------+--------------------+---------------+--------------------------------------+
   | guass        | mean,stddev        | min,max       | "gauss(mean=2, stddev=1)"            |
   +--------------+--------------------+---------------+--------------------------------------+
   | guassian     |                    |               | "guassian(mean=7, stddev=1, min=4)"  |
   +--------------+--------------------+---------------+--------------------------------------+
   | normal       |                    |               | "normal(mean=25, stddev=10, max=40)" |
   +--------------+--------------------+---------------+--------------------------------------+

Prototype:

.. code-block:: python

    {
      "<field name>": {
        "type": "distribution",
        "data": "<dist func name>(<param1>=<val1>, ..., <paramN>=<valN>)
      }
    }

Examples:

.. code-block:: json

    {
      "values": {
        "type": "distribution",
        "data": "uniform(start=10, end=30)"
      }
    }

.. code-block:: json

    {
      "ages": {
        "type": "distribution",
        "data": "normal(mean=28, stddev=10, min=18, max=40)"
      }
    }

.. code-block:: json

    {
      "pressure": {
        "type": "distribution",
        "data": "gauss(mean=33, stddev=3.4756535)",
        "config": {
          "count_dist": "normal(mean=2, stddev=1, min=1, max=4)",
          "as_list": true
        }
      }
    }

A ``distribution`` type field with a uniform distribution will produce similar values to a ``rand_range`` field. With
rand_range it is easier to specify a specific number of decimal places to keep. To do this for the distribution type,
you need to make use of the ``cast`` config with a ``roundN`` :ref:`caster<casters>`. See example below.

.. code-block:: json

   {
     "values1": {
       "type": "rand_range",
       "data": [10, 30, 4]
     },
     "values2": {
       "type": "distribution",
       "data": "uniform(start=10, end=30)",
       "config": {
         "cast": "round4"
       }
     },
     "values3:rand_range": [10, 30, 4],
     "values4:distribution?cast=round4": "uniform(start=10, end=30)"
   }


.. code-block:: shell

   $ datagen -s spec.json -i2 --log-level off --printkey
   values1 -> 29.7907
   values2 -> 18.9114
   values3 -> 13.5495
   values4 -> 15.5935
   values1 -> 22.0634
   values2 -> 17.8552
   values3 -> 22.982
   values4 -> 20.5616