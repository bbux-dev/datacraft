geo types
---------

There are three main geo types: ``geo.lat``, ``geo.long``, and ``geo.pair``. The defaults will create decimal string
values in the valid ranges: -90 to 90 for latitude and -180 to 180 for longitude. You can bound the ranges in several
ways. The first is with the start_lat, end_lat, start_long, end_long config params. These will set the individual
bounds for each of the segments. You can use one or more of them. The other mechanism is by defining a bbox array
which consists of the lower left geo point and the upper right one.

.. list-table::
   :header-rows: 1

   * - type
     - param
     - description
   * - all
     - precision
     - number of decimal places for lat or long, default is 4
   * -
     - bbox
     - array of [min Longitude, min Latitude, max Longitude, max Latitude]
   * - geo.lat
     - start_lat
     - lower bound for latitude
   * -
     - end_lat
     - upper bound for latitude
   * - geo.long
     - start_long
     - lower bound for longitude
   * -
     - end_long
     - upper bound for longitude
   * - geo.pair
     - join_with
     - delimiter to join long and lat with, default is comma
   * -
     - as_list
     - One of yes, true, or on if the pair should be returned as a list instead of as a joined string
   * -
     - lat_first
     - if latitude should be first in the generated pair, default is longitude first
   * -
     - start_lat
     - lower bound for latitude
   * -
     - end_lat
     - upper bound for latitude
   * -
     - start_long
     - lower bound for longitude
   * -
     - end_long
     - upper bound for longitude


Prototype:

.. code-block:: python

    {
      "<field name>": {
        "type": "geo.lat",
        or
        "type": "geo.long",
        or
        "type": "geo.pair",
        "config": {
          "key": Any
        }
      }
    }

Examples:

.. code-block:: json

    {
      "egypt": {
        "type": "geo.pair",
        "config": {
          "bbox": [
            31.33134,
            22.03795,
            34.19295,
            25.00562
          ],
          "precision": 3
        }
      }
    }