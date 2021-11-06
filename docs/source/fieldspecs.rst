Field Specs
===========

Field Spec Structure
--------------------

There are several ways to define a Field Spec. There is the full spec format,
and a variety of short hand notations.

The Full Format
^^^^^^^^^^^^^^^

Each of the core built in types has a JSON schema.  The full format is what is used
to validate against this schema. Other shorthand formats are processed into the full
format. Each Type Handler requires different pieces of information. For most types,
the key fields are ``type``, ``data``, and ``config``. Below is the general Field
Spec structure.

.. code-block::

   {
     "type": "<the type>",
     "config": {
       "key1": "value1",
       ...
       "keyN": "valueN"
     },
     "data": ["the data"],
     "ref": "REF_POINTER_IF_USED",
     "refs": ["USES", "MORE", "THAN", "ONE"],
     "fields": { "for": {}, "nested": {}, "types": {} }
   }

Values Shorthand
^^^^^^^^^^^^^^^^

The ``values`` type is very common and so has a shorthand notation. Below is an
example full Field Spec for some values types fields and the same spec in
shorthand notation.

.. code-block:: json

   {
     "field1": {
       "type": "values",
       "data": [1, 2, 3, 4, 5]
     },
     "field2": {
       "type": "values",
       "data": {"A": 0.5, "B": 0.3, "C": 0.2}
     },
     "field3": {
       "type": "values",
       "data": "CONSTANT"
     }
   }

.. collapse:: YAML Spec

    .. code-block:: yaml

       field1:
         type: values
         data: [1, 2, 3, 4, 5]
       field2:
         type: values
         data: {A: 0.5, B: 0.3, C: 0.2}
       field3:
         type: values
         data: CONSTANT

.. collapse:: API Example

    .. code-block:: python

       import datagen

       spec_builder = datagen.spec_builder()

       spec_builder.add_field('field1', dataspec.builder.values([1, 2, 3, 4, 5]))
       spec_builder.add_field('field2', dataspec.builder.values({"A": 0.5, "B": 0.3, "C": 0.2}))
       spec_builder.add_field('field3', dataspec.builder.values("CONSTANT"))

       spec = spec_builder.build()


**Shorthand Format:**

.. code-block:: json

   {
     "field1": [1, 2, 3, 4, 5],
     "field2": {
       "A": 0.5,
       "B": 0.3,
       "C": 0.2
     },
     "field3": "CONSTANT"
   }

.. collapse:: YAML Spec

    .. code-block:: yaml

       field1: [1, 2, 3, 4, 5]
       field2:
         A: 0.5
         B: 0.3
         C: 0.2
       field3: CONSTANT

.. collapse:: API Example

    .. code-block:: python

       import datagen

       spec_builder = datagen.spec_builder()

       spec_builder.add_field('field1', [1, 2, 3, 4, 5])
       spec_builder.add_field('field2', {"A": 0.5, "B": 0.3, "C": 0.2})
       spec_builder.add_field('field3', "CONSTANT")

       spec = spec_builder.build()


The value after the field name is just the value of the data element from the
full Field Spec. Config params can be added to the key using the URL syntax
described below.

Inline Key Type Shorthand
^^^^^^^^^^^^^^^^^^^^^^^^^

Some specs lend themselves to being easily specified with few parameters. One
short hand way to do this is the use a colon in the key to specify the type
after the field name. For example ``{"id:uuid":{}}``. This says the field ``id`` is
of type ``uuid`` and has no further configuration. If no type is specified, the
field is assumed to be a ``values`` type.

Inline Key Config Shorthand
^^^^^^^^^^^^^^^^^^^^^^^^^^^

It is also possible to specify configuration parameters in the key by using URL
style parameters. For example.


.. collapse:: JSON Spec

    .. code-block:: json

       {
         "network:ipv4?cidr=192.168.0.0/16": {}
       }

.. collapse:: YAML Spec

    .. code-block:: yaml

        network:ipv4?cidr=192.168.0.0/16: {}

.. collapse:: API Example

    .. code-block:: python

       import datagen

       spec_builder = datagen.spec_builder()

       spec_builder.add_field("network:ipv4?cidr=192.168.0.0/16", {})

       spec = spec_builder.build()


The ``network`` field is of type ``ipv4`` and the required ``cidr`` param is specified
in the key.

Spec Configuration
------------------

There are two ways to configure a spec. One is by providing a ``config`` element
in the Field Spec and the other is by using a URL parameter format in the key.
For example, the following two fields will produce the same values:


.. collapse:: JSON Spec

    .. code-block:: json

       {
         "ONE": {
           "type": "values",
           "data": [1, 2, 3],
           "config": {
             "prefix": "TEST",
             "suffix": "@DEMO"
           }
         },
         "TWO?prefix=TEST&suffix=@DEMO": {
           "type": "values",
           "data": [1, 2, 3]
         }
       }

.. collapse:: YAML Spec

    .. code-block:: yaml

       ONE:
         type: values
         data: [1, 2, 3]
         config:
           prefix: TEST
           suffix: '@DEMO'
       TWO?prefix=TEST&suffix=@DEMO:
         type: values
         data: [1, 2, 3]

.. collapse:: API Example

    .. code-block:: python

       import datagen

       spec_builder = datagen.spec_builder()

       spec_builder.values('ONE', [1, 2, 3], prefix='TEST', suffix='@DEMO')
       spec_builder.values('TWO?prefix=TEST&suffix=@DEMO', [1, 2, 3])

       spec = spec_builder.build()


Common Configurations
^^^^^^^^^^^^^^^^^^^^^

There are some configuration values that can be applied to all or a subset of
types. These are listed below

.. list-table::
   :header-rows: 1

   * - key
     - argument
     - effect 
   * - prefix
     - string
     - Prepends the value to all results
   * - suffix
     - string
     - Appends the value to all results
   * - quote
     - string
     - Wraps the resulting value on both sides with the provided string
   * - cast
     - i,int,f,float,s,str,string
     - For numeric types, will cast results the provided type
   * - join_with
     - string
     - For types that produce multiple values, use this string to join them
   * - as_list
     - yes,true,on
     - For types that produce multiple values, return as list without joining


Example:

.. collapse:: JSON Spec

    .. code-block:: json

       {
         "field": {
           "type": "values",
           "data": ["world", "beautiful", "destiny"],
           "config": {
             "prefix": "hello "
           }
         }
       }

.. collapse:: YAML Spec

    .. code-block:: yaml

       field:
         type: values
         data: [world, beautiful, destiny]
         config:
           prefix: 'hello '

.. collapse:: API Example

    .. code-block:: python

       import datagen

       spec_builder = datagen.spec_builder()

       spec_builder.values('field',
                           ["world", "beautiful", "destiny"],
                           prefix='hello ')

       spec = spec_builder.build()


Count Config Parameter
^^^^^^^^^^^^^^^^^^^^^^

Several types support a ``count`` config parameter. The value of the count
parameter can be any of the supported values specs formats. For example a
constant ``3``\ , list ``[2, 3, 7]``\ , or weighted
map ``{"1": 0.5, "2": 0.3, "3": 0.2 }``. This will produce the number of values by
creating a value supplier for the count based on the supplied parameter. Most of
the time if the count is greater than 1, the values will be returned as an
array. Some types support joining the values by specifying the ``join_with``
parameter. Some types will let you explicitly set the ``as_list`` parameter to
force the results to be returned as an array and not the default for the given
type.

Count Distributions
^^^^^^^^^^^^^^^^^^^

Another way to specify a count is to use a count distribution. This is done with
the ``count_dist`` param.  The param takes a string argument which is the
distribution along with its required arguments in function call form with
parameters explicitly named.  See the table below.

.. list-table::
   :header-rows: 1

   * - distribution
     - required arguments
     - optional args
     - examples
   * - uniform
     - start,end
     - 
     - "uniform(start=10, end=30)"
   * -
     - 
     - 
     - "uniform(start=1, end=3)"
   * - guass
     - mean,stddev
     - min,max
     - "gauss(mean=2, stddev=1)"
   * - guassian
     - 
     - 
     - "guassian(mean=7, stddev=1, min=4)"
   * - normal
     - 
     - 
     - "normal(mean=25, stddev=10, max=40)"


``normal``\ , ``guassian``\ , and ``gauss`` are all aliases for a
`Normal Distribution <https://en.wikipedia.org/wiki/Normal_distribution>`_.

Example:

.. collapse:: JSON Spec

    .. code-block:: json

       {
         "field": {
           "type": "char_class",
           "data": "visible",
           "config": {
             "count_dist": "normal(mean=5, stddev=2, min=1, max=9)"
           }
         }
       }

.. collapse:: YAML Spec

    .. code-block:: yaml

       field:
         type: char_class
         data: visible
         config:
           count_dist: normal(mean=5, stddev=2, min=1, max=9)

.. collapse:: API Example

    .. code-block:: python

       import datagen

       spec_builder = datagen.spec_builder()

       spec_builder.char_class(key='field',
                               data='visible',
                               count_dist='normal(mean=5, stddev=2, min=1, max=9)')

       spec = spec_builder.build()

