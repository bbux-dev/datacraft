date
----

A Date Field Spec is used to generate date strings. The default format is day-month-year i.e. Christmas 2050 would
be: 25-12-2050. There is also a `date.iso` type that generates ISO8601 formatted date strings without microseconds
and a `date.iso.us` for one that generates them with microseconds. We use the `format specification <https://docs
.python.org/3/library/datetime.html#strftime-and-strptime-format-codes>`_ from the datetime module.

Uniformly Sampled Dates
^^^^^^^^^^^^^^^^^^^^^^^

The default strategy is to create random dates within a 30 day range, where the start date is today. You can use the
``start`` parameter to set a specific start date for the dates. You can also explicitly specify an ``end`` date. The
``start`` and ``end`` parameters should conform to the specified date format, or the default
if none is provided. The ``offset`` parameter can be used to shift the dates by a specified number of days. A
positive ``offset`` will shift the start date back. A negative ``offset`` will shift the date forward. The
``duration_days`` parameter can be used to specify the number of days that should be covered in the date range,
instead of the default 30 days. This parameter is usually specified as an integer constant.

.. code-block:: text

       start                              end (default start + 30 days)
          |--------------------------------|
  |+offset|                           start+duration_days
  |--------------------------------|
          |-offset|
                  |--------------------------------|


Dates Distributed around a Center Point
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

An alternative strategy is to specify a ``center_date`` parameter with an optional ``stddev_days``. This will create
a normal or gaussian distribution of dates around the center point.

.. code-block:: text

                       |
                       |
                    |  |  |
                 |  |  |  |  |
              |  |  |  |  |  |  |
     |  |  |  |  |  |  |  |  |  |  |  |  |
    |-------------------------------------|
    |         | stddev | stddev |         |
                    center


Restricting Hours
^^^^^^^^^^^^^^^^^

If you want your generated dates to be restricted to certain hours of the day, you provide the ``hours`` config param.
The value of this parameter can be any type of Field Spec that produces valid integers in the range of 0 to 23. See
examples below.

Prototype:

.. code-block:: python

    {
      "<field name>": {
        "type": "date",
        OR,
        "type": "date.iso",
        OR,
        "type": "date.iso.us",
        "config": {
          "format": "Valid datetime format string",
          "duration_days": "The number of days from the start date to create date strings for",
          "start": "date string matching format or default format to use for start date",
          "end": "date string matching format or default  format to use for end date",
          "offset": "number of days to shift base date by, positive means shift backwards, negative means forward",
          "center_date": "date string matching format or default format to use for center date",
          "stddev_days": "The standard deviation in days from the center date that dates should be distributed",
          "hours": "spec describing how the hours should be populated, i.e. only between 9am and 5pm"
        }
      }
    }

Examples:

.. code-block:: json

    {
      "dates": {
        "type": "date",
        "config": {
          "duration_days": "90",
          "start": "15-Dec-2050 12:00",
          "format": "%d-%b-%Y %H:%M"
        }
      }
    }

.. code-block:: json

    {
      "dates": {
        "type": "date",
        "config": {
          "center_date": "20500601 12:00",
          "format": "%Y%m%d %H:%M",
          "stddev_days": "2"
        }
      }
    }

.. code-block:: json

    {
      "start_time": {
        "type": "date",
        "config": {
          "center_date": "20500601 12:00",
          "format": "%Y%m%d %H:%M",
          "hours": { "type": "values", "data": { "7": 0.1, "8": 0.2, "9": 0.4, "10": 0.2, "11": 0.1 }
        }
      }
    }
