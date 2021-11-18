Examples
========

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

    datagen -s insults.json -i 100 | grep '1,' | tail
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
just to get test data, it is possible to simulate the data fairly easy by creating a template and a Data Spec to
populate the template with.  Below is an example GeoJSON that contains the location of Paris France along with some
metadata about it.

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
the ``refs`` section of the spec and use a ``configref`` to store the common config information for each field.

.. code-block:: json

    {
      "refs": {
        "NAME": {
          "type": "csv",
          "config": {
            "configref": "CITY_FILE_CONFIG",
            "column": 1,
            "quote": "\""
          }
        },
        "LAT:csv?configref=CITY_FILE_CONFIG&column=3&cast=float": {},
        "LONG:csv?configref=CITY_FILE_CONFIG&column=4&cast=float": {},
        "COUNTRY:csv?configref=CITY_FILE_CONFIG&column=5&quote=\"": {},
        "POP:csv?configref=CITY_FILE_CONFIG&column=10&cast=int": {},
        "CITY_FILE_CONFIG": {
          "type": "configref",
          "config": {
            "datafile": "worldcities.csv",
            "headers": true,
            "sample_rows": true
          }
        }
      }
    }

The NAME field is defined using the full spec format, while there rest are defined with the short hand notation.
Notice for the LAT and LONG, fields that they are cast to floating point values, since by default all csv data is
read in as a string.  We define a CITY_FILE_CONFIG reference that holds the name of the datafile that contains the csv
data values. The ``sample_rows`` configuration parameter will ensure that the cities are selected at random from our
csv file, but are consistent across rows in the file.

The next thing that needs to be done is define the features field.  This is a nested field that has two sub fields:
``geometry`` and ``properties``, which are also nested fields:

.. code-block:: json

    {
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
ensure that the result is iterable. Second the ``count`` parameter is defined as a weighted value spec. This means that
60% of the time there will be a single feature, 30% there will be 2, and 10% there will be 3. If only a single
feature was desired, the count config parameter could be left out or hard coded to 1. To simplify and de-clutter the
spec the definition of the geometry and properties fields are externalized as ``ref`` types. Here is the definition
for those two refs:

.. code-block:: json

    {
      "refs": {
        "GEOMETRY:nested": {
          "fields": {
            "geo_type": "Point",
            "lat:ref": "LAT",
            "long:ref": "LONG"
          }
        },
        "PROPERTIES:nested": {
          "fields": {
            "name:ref": "NAME",
            "country:ref": "COUNTRY",
            "population:ref": "POP"
          },
          "field_groups": {
            "0.8": ["name", "country", "population"],
            "0.2": ["name", "country"],
          }
        },
        "...": "..."
      }
    }

Both ``GEOMETRY`` and ``PROPERTIES`` are nested fields. The ``geometry`` element has a field called type.  ``type`` is
currently a reserved key word in DataSpecs, so can't be used as a field name. The field is named geo_type instead and
the value is set to a constant value "Point". There are other types of geometry, but for this demo we are only
producing points. The lat and long field are supplied from the csv fie using the references that were defined earlier.
The properties values also come from the references defined earlier.  The ``PROPERTIES`` reference is a nested type
and has another property defined ``field_groups``.  These are explained in detail in :ref:`FieldGroups<field_groups>`
The type here is a weighted one. 80% of the records will contain all three fields in the properties and 20% of the
time there will only be two.

If we run the spec as is this is an example of the data that is produced:

.. code-block:: shell

    $ datagen -s spec.json -d data -i 1 --log-level off -x --format json-pretty

.. code-block:: json

    {
        "features": [
            {
                "geometry": {
                    "geo_type": "Point",
                    "lat": 52.6624,
                    "long": 5.2
                },
                "properties": {
                    "name": "\"Venhuizen\"",
                    "country": "\"Netherlands\"",
                    "population": 7828
                }
            }
        ]
    }

This is close to the desired GeoJSON format but not quite.  We need to use this data to populate a template. The art
of writing `Jinja2 <https://pypi.org/project/Jinja2/>`_ templates is beyond the scope of this example.  Below is our
template for creating GeoJSON from our example Data Spec:

.. code-block:: python

    {
      "type": "FeatureCollection",
      "features": [
    {%- for feature in features %}
        {
          "type": "Feature",
          "geometry": {
            "type": "{{ feature['geometry']['geo_type'] }}",
            "coordinates": [{{ feature['geometry']['long'] }}, {{ feature['geometry']['lat'] }}]
          },
          "properties": {
      {%- for key, value in feature['properties'].items() %}
            "{{ key }}": {{ value }}{% if not loop.last %},{% endif %}
      {%- endfor %}
          }
        }{% if not loop.last %},{% endif %}
    {%- endfor %}
      ]
    }

Running the earlier command and specifying this template produces:

.. code-block:: shell

    $ datagen -s spec.json -d data -i 1 --log-level off -x -t geojson.jinja

.. code-block:: json

    {
      "type": "FeatureCollection",
      "features": [
        {
          "type": "Feature",
          "geometry": {
            "type": "Point",
            "coordinates": [13.2167, 46.2167]
          },
          "properties": {
            "name": "Tarcento",
            "country": "Italy",
            "population": 8964
          }
        },
        {
          "type": "Feature",
          "geometry": {
            "type": "Point",
            "coordinates": [174.95, -37.2667]
          },
          "properties": {
            "name": "Tuakau",
            "country": "New Zealand",
            "population": 5390
          }
        }
      ]
    }

.. collapse:: Full Version of Data Spec

  .. code-block:: json

    {
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
      "refs": {
        "GEOMETRY:nested": {
          "fields": {
            "geo_type:values": "Point",
            "lat:ref": "LAT",
            "long:ref": "LONG"
          }
        },
        "PROPERTIES:nested": {
          "fields": {
            "name:ref": "NAME",
            "country:ref": "COUNTRY",
            "population:ref": "POP"
          },
          "field_groups": {
            "0.8": ["name", "country", "population"],
            "0.2": ["name", "country"],
          }
        },
        "NAME": {
          "type": "csv",
          "config": {
            "configref": "CITY_FILE_CONFIG",
            "column": 1,
            "quote": "\""
          }
        },
        "NAME2:csv?configref=CITY_FILE_CONFIG&column=1&quote=\"": {},
        "LAT:csv?configref=CITY_FILE_CONFIG&column=3&cast=float": {},
        "LONG:csv?configref=CITY_FILE_CONFIG&column=4&cast=float": {},
        "COUNTRY:csv?configref=CITY_FILE_CONFIG&column=5&quote=\"": {},
        "POP:csv?configref=CITY_FILE_CONFIG&column=10&cast=int": {},
        "CITY_FILE_CONFIG": {
          "type": "configref",
          "config": {
            "datafile": "worldcities.csv",
            "headers": true,
            "sample_rows": true
          }
        }
      }
    }
