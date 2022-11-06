date
----

A Date Field Spec is used to generate date strings. The default format is day-month-year i.e. Christmas 2050 would
be: 25-12-2050. There is also a `date.iso` type that generates ISO8601 formatted date strings without microseconds
and a `date.iso.us` for one that generates them with microseconds. There are also a `date.epoch` and `date.epcoh.ms`
and `date.epoch.millis`. These are for generating unix epoch timestamps. We use the
`format specification <https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes>`_
from the datetime module.

.. list-table::
   :header-rows: 1

   * - type
     - example output
   * - date
     - 11-18-2050
   * - date.iso
     - 2050-12-01T01:44:35
   * - date.iso.ms
     - 2050-12-01T05:11:20.543
   * - date.iso.millis
     - 2050-12-01T05:11:20.543
   * - date.iso.us
     - 2050-12-01T06:19:02.752373
   * - date.iso.micros
     - 2050-12-01T06:17:05.487878
   * - date.epoch
     - 1669825519
   * - date.epoch.ms
     - 1668624934547
   * - date.epoch.millis
     - 1669166880466

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
        "type": "date.iso.ms",
        OR,
        "type": "date.iso.millis",
        OR,
        "type": "date.iso.us",
        OR,
        "type": "date.iso.micros",
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

Dates that start on 15 Dec 2050 and span a 90 day period

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

Dates centered on 01 Jun 2050 with a standard deviation of +-2 days

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

ISO Date Centered at 1 Jun 2050, with weighted hours of the day

.. code-block:: json

    {
      "start_time": {
        "type": "date.iso",
        "config": {
          "center_date": "2050-06-01T12:00:00",
          "hours": { "type": "values", "data": { "7": 0.1, "8": 0.2, "9": 0.4, "10": 0.2, "11": 0.1 } }
        }
      }
    }

Epoch Date with milliseconds 14 days in the future with a 7 day window for timestamps

.. code-block:: json

    {
      "start_time": {
        "type": "date.epoch.ms",
        "config": {
          "offset": -14,
          "duration_days": 7
        }
      }
    }
