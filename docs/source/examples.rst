Examples
========

Unit Test Data
--------------

Datacraft is ideal for generating test data that conforms to a specific structure while minimizing the details of the
values in the structure. A common way to externalize complex data from a unit test is by the use of fixtures. Below is
an example pytest fixture that will create a Data Spec that can be used to generate multiple records. These records
can then be passed to processing logic to verify functionality.  This is usually much more compact and flexible then
hard coding a bunch of examples.  It is also easier to update the test data when the structure of the records changes.


.. code-block:: python

   @pytest.fixture
   def example_good_record():
       raw = {
           "id": {"type": "uuid"},
           "handle:ref": "HANDLE",
           "joined": {"type": "date.iso"},
           "follows:ref": {
               "ref": "HANDLE",
               "config": {
                   "as_list": True,
                   "count_dist": "normal(mean=10, stddev=5, min=1, max=100)"
               }
           },
           "refs": {
               "HANDLE": {
                   "type": "rand_int_range",
                   "data": [0, 1000],
                   "config": {"prefix": "user"}
               }
           }
       }
       spec = datacraft.parse_spec(raw)
       return spec


   def test_good_record(example_good_record):
       records = list(example_good_record.generator(10))
       success = my_function(records)
       assert success is True


Generating Sentences
--------------------

When training a Machine Learning Classifier, it can be difficult to create labeled data from scratch.  By analyzing
the structure of the data it may be possible to augment a small initial set of examples by generating additional
similar data that follows the same structure. For example, we want to create an Insult detector. Let's say these are
the initial examples we have:

.. code-block:: text

   1,You are such a schmuck
   1,You're a complete and utter moron
   1,You're so stupid
   1,You're an idiot
   0,You are such a blessing
   0,You're a complete and utter help
   0,You're so cute
   0,You're an insperation

By examining these sentences we can get an idea of the general structure of an insult.  We might break it down like this.

.. code-block:: text

   PRONOUN_IDENTIFIER ADVERB_MODIFIER ADJECTIVE_INSULT
         You are           so             stupid

   PRONOUN_IDENTIFIER DETERMINANT NOUN_INSULT
         You're            an        idiot

To generate more sample sentences, we would just need to fill in examples for each of the identified parts.  Our spec
might look like:

.. code-block:: json

   {
     "insults1": {
       "type": "combine",
       "refs": ["PRONOUN_IDENTIFIER", "ADVERB_MODIFIER", "ADJECTIVE_INSULT"],
       "config": { "join_with": " ", "prefix": "1,"}
     },
     "insults2": {
       "type": "combine",
       "refs": ["PRONOUN_IDENTIFIER", "DETERMINANT", "NOUN_INSULT"],
       "config": { "join_with": " ", "prefix": "1,"}
     },
     "compliments1": {
       "type": "combine",
       "refs": ["PRONOUN_IDENTIFIER", "ADVERB_MODIFIER", "ADJECTIVE_COMPLIMENT"],
       "config": { "join_with": " ", "prefix": "0,"}
     },
     "compliments2": {
       "type": "combine",
       "refs": ["PRONOUN_IDENTIFIER", "DETERMINANT", "NOUN_COMPLIMENT"],
       "config": { "join_with": " ", "prefix": "0,"}
     },
     "refs":{
       "PRONOUN_IDENTIFIER": ["You are", "You're"],
       "ADVERB_MODIFIER": ["so", "extremely", "utterly", "incredibly"],
       "DETERMINANT": {"a":  0.3, "an": 0.3, "such a": 0.3, "a complete and utter": 0.1},
       "ADJECTIVE_INSULT": ["stupid", "dumb", "idiotic", "imbecilic", "useless", "ugly"],
       "NOUN_INSULT": ["idiot", "schmuck", "moron", "imbecile", "poop face"],
       "ADJECTIVE_COMPLIMENT": ["nice", "sweet", "kind", "smart"],
       "NOUN_COMPLIMENT": ["inspiration", "blessing", "friend"]
     }
   }

Looking at some of the insults produced

.. code-block:: text

    datacraft -s insults.json -i 100 | grep '1,' | tail
    1,You're incredibly ugly
    1,You're a idiot
    1,You are so stupid
    1,You are an schmuck
    1,You're extremely dumb
    1,You're an moron
    1,You are utterly idiotic
    1,You are a imbecile
    1,You're incredibly imbecilic
    1,You're a poop face

Generating GeoJSON
------------------

`GeoJSON <https://en.wikipedia.org/wiki/GeoJSON>`_ is a common format used in Geo oriented data processing and services.
If interacting with a service that serves up GeoJSON, and you didn't want to hammer the service over and over
just to get test data, it is possible to simulate the data fairly easy by creating a Data Spec to simulate the data
with.  Below is an example GeoJSON that contains the location of Paris France along with some metadata about
it.

.. code-block:: json

    {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [2.3522, 48.8566]
                },
                "properties": {
                    "name": "PARIS",
                    "country": "FR",
                    "population": 2175601
                }
            }
        ]
    }

The parts that vary in the GeoJSON are the ``features`` and the metadata in them. It would be ideal to generate the
coordinates and metadata so that they match valid locations.  The easiest way to do this is to use an external csv
file to hold the bulk of the information.

If you use the free version of the data from https://simplemaps.com/data/world-cities, you can reference this from a
Data Spec using the csv type. We will put the fields, ``name``, ``lat``, ``long``, ``country``, and ``population`` in
the ``refs`` section of the spec using a ``csv_select`` type to store the common config information for each field.

.. code-block:: json

    {
      "refs": {,
        "CITIES_CSV": {
          "type": "csv_select",
          "data": {
            "NAME": 2,
            "LATITUDE": 3,
            "LONGITUDE": 4,
            "COUNTRY": 5,
            "POPULATION": 10
          },
          "config": {
            "datafile": "{{ csv_file }}",
            "headers": true,
            "sample_rows": true
          }
        }
      }
    }

To simplify our spec, a :ref:`csv_select<csv_core_types>` type field spec is used to define the various fields from the
csv we want to use. The ``sample_rows`` configuration parameter will ensure that the cities are selected at random
from our csv file, but are consistent across rows in the file. We also template the name of the datafile to use. This
simplifies testing the spec by allowing us to specify different csv files to use for data population.  The ``-v`` or
``--vars csv_file=filename.csv`` command line args must be specified in order for this value to be properly populated.

The next thing that needs to be done is define the features field.  This is a nested field that has two sub fields:
``geometry`` and ``properties``, which are also nested fields:

.. code-block:: json

    {
      "type": "FeatureCollection",
      "features": {
        "type": "nested",
        "config": {
          "as_list": true,
          "count": {
            "1": 0.6,
            "2": 0.3,
            "3": 0.1
          }
        },
        "fields": {
          "geometry:ref": "GEOMETRY",
          "properties:ref": "PROPERTIES"
        }
      },
      "refs": "..."
    }

Two important things to note. First the config param ``as_list`` is set to true for the features field. This will
ensure that the result is a list. Second the ``count`` parameter is defined as a weighted value spec. This means that
60% of the time there will be a single feature, 30% there will be 2, and 10% there will be 3. If only a single
feature was desired, the count config parameter could be left out or hard coded to 1. To simplify and de-clutter the
spec the definition of the geometry and properties fields are externalized as ``ref`` types. Here is the definition
for those two refs:

.. code-block:: json

    {
      "refs": {
        "GEOMETRY:nested": {
          "fields": {
            "type": "Point",
            "lat:ref?cast=float": "LATITUDE",
            "long:ref?cast=float": "LONGITUDE"
          }
        },
        "PROPERTIES:nested": {
          "fields": {
            "name:ref": "NAME",
            "country:ref": "COUNTRY",
            "population:ref?cast=int": "POPULATION"
          },
          "field_groups": {
            "0.8": ["name", "country", "population"],
            "0.2": ["name", "country"]
          }
        },
        "...": "..."
      }
    }

Both ``GEOMETRY`` and ``PROPERTIES`` are nested fields. The ``geometry`` element has a field called type and
the value is set to a constant value "Point". There are other types of geometry, but for this demo we are only
producing points. The lat and long field are supplied from the csv file using the references that were defined
earlier. These values need to be cast to floating point numbers, which we do by specifying: ``?cast=float``.
The properties values also come from the references defined earlier.  The ``PROPERTIES`` reference is a nested type
and has another property defined ``field_groups``.  These are explained in detail in :ref:`FieldGroups<field_groups>`
The type here is a weighted one. 80% of the records will contain all three fields in the properties and 20% of the
time there will only be two.

When running datacraft for this spec, set the ``-i`` or ``--iterations`` argument to 1, since the complete
structure is encapsulated in a single record.  By default, when writing the output as JSON, the records are
output as a list, even when there is only one record to output.  We can get past this by setting the ``-r`` or
``--records-per-file`` arg to 1 also.  The complete command to use is shown below with an example of the output that
is produced:

.. code-block:: shell

    $ datacraft -s spec.json -d data -i 1 -r 1 --log-level off -x --format json-pretty -v csv_file=worldcities.csv

.. code-block:: json

   {
       "type": "FeatureCollection",
       "features": [
           {
               "geometry": {
                   "type": "Point",
                   "lat": 22.9958,
                   "long": -98.9447
               },
               "properties": {
                   "name": "Xicoténcatl",
                   "country": "Mexico"
               }
           },
           {
               "geometry": {
                   "type": "Point",
                   "lat": 40.7186,
                   "long": -4.2478
               },
               "properties": {
                   "name": "El Espinar",
                   "country": "Spain",
                   "population": 9086
               }
           }
       ]
   }

This is exactly the format we want.  You can use the ``--server`` command line flag to stand up a Flask REST end
point that will return the GeoJSON. Be sure to set the python encoding to UTF-8 when serving up the data
(``export PYTHONUTF8=1`` or ``set PYTHONUTF8=1``). If using powershell this may mean setting the encoding on the
shell itself to UTF-8.


.. code-block:: shell

    $ datacraft -s spec.json -d data -i 1 -r 1 --log-level off -x --format json-pretty -v csv_file=worldcities.csv --server


.. collapse:: Full Version of Data Spec

  .. code-block:: json

   {
     "type": "FeatureCollection",
     "features": {
       "type": "nested",
       "config": {
         "as_list": true,
         "count": { "1": 0.6, "2": 0.3, "3": 0.1 }
       },
       "fields": {
         "geometry:ref": "GEOMETRY",
         "properties:ref": "PROPERTIES"
       }
     },
     "refs": {
       "GEOMETRY:nested": {
         "fields": {
           "type": "Point",
           "lat:ref?cast=float": "LATITUDE",
           "long:ref?cast=float": "LONGITUDE"
         }
       },
       "PROPERTIES:nested": {
         "fields": {
           "name:ref": "NAME",
           "country:ref": "COUNTRY",
           "population:ref?cast=int": "POPULATION"
         },
         "field_groups": {
           "0.8": ["name", "country", "population"],
           "0.2": ["name", "country"]
         }
       },
       "CITIES_CSV": {
         "type": "csv_select",
         "data": {
           "NAME": 2,
           "LATITUDE": 3,
           "LONGITUDE": 4,
           "COUNTRY": 5,
           "POPULATION": 10
         },
         "config": {
           "datafile": "{{ csv_file }}",
           "headers": true,
           "sample_rows": true
         }
       }
     }
   }
