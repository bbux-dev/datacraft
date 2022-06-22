Field Specs
===========

Field Spec Structure
--------------------

There are several ways to define a Field Spec. There is the full spec format, and a variety of short hand notations.

The Full Format
^^^^^^^^^^^^^^^

Each of the :doc:`core built in types<coretypes>` has a JSON schema.  The full format is what is used to validate
against this schema. Other shorthand formats are processed into the full format. Each Type Handler requires different
pieces of information. For most types, the key fields are ``type``, ``data``, and ``config``. Below is the general Field
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

The ``values`` type is very common and so has a shorthand notation. Below is an example full Field Spec for some
values types fields and the same spec in shorthand notation.

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

The value after the field name is just the value of the data element from the full Field Spec. Config params can be
added to the key using the URL syntax described below.

Inline Key Type Shorthand
^^^^^^^^^^^^^^^^^^^^^^^^^

Some specs lend themselves to being easily specified with few parameters. One short hand way to do this is the use a
colon in the key to specify the type after the field name. For example ``{"id:uuid":{}}``. This says the field ``id`` is
of type ``uuid`` and has no further configuration. If no type is specified, the field is assumed to be a ``values``
type.

Inline Key Config Shorthand
^^^^^^^^^^^^^^^^^^^^^^^^^^^

It is also possible to specify configuration parameters in the key by using URL style parameters. For example.

.. code-block:: json

   {
     "network:ipv4?cidr=192.168.0.0/16": {}
   }

The ``network`` field is of type ``ipv4`` and the required ``cidr`` param is specified in the key.

Spec Configuration
------------------

There are two ways to configure a spec. One is by providing a ``config`` element in the Field Spec and the other is
by using a URL parameter format in the key. For example, the following two fields will produce the same values:


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

Common Configurations
^^^^^^^^^^^^^^^^^^^^^

There are some configuration values that can be applied to all or a subset of types. These are listed below

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

Count Config Parameter
^^^^^^^^^^^^^^^^^^^^^^

Several types support a ``count`` config parameter. The value of the count parameter can be any of the supported
values specs formats. For example a constant ``3``\ , list ``[2, 3, 7]``\ , or weighted map ``{"1": 0.5, "2": 0.3,
"3": 0.2 }``. This will produce the number of values by creating a value supplier for the count based on the supplied
parameter. Most of the time if the count is greater than 1, the values will be returned as an array. Some types
support joining the values by specifying the ``join_with`` parameter. Some types will let you explicitly set the
``as_list`` parameter to force the results to be returned as an array and not the default for the given type.

Count Distributions
^^^^^^^^^^^^^^^^^^^

Another way to specify a count is to use a count distribution. This is done with the ``count_dist`` param.  The param
takes a string argument which is the distribution along with its required arguments in function call form with
parameters explicitly named.  See the table below.

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

``normal``\ , ``guassian``\ , and ``gauss`` are all aliases for a
`Normal Distribution <https://en.wikipedia.org/wiki/Normal_distribution>`_.

Example:

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

.. _custom_count_dist:

Custom Count Distributions
^^^^^^^^^^^^^^^^^^^^^^^^^^

Custom distributions can be supplied using :ref:`custom code<custom_code>` loading and the
``@datacraft.registry.distribution`` decorator:

.. tabs::

   .. tab:: Custom Code

      .. code-block:: python

         from scipy.stats import gamma
         import datacraft

         class _GammaDist(datacraft.Distribution):
             def __init__(self, a: float):
                 self.a = a

             def next_value(self):
                 return gamma.rvs(self.a)

         @datacraft.registry.distribution('gamma')
         def _gamma_distribution(a, **kwargs) -> datacraft.Distribution:
             """ example custom distribution """
             return _GammaDist(float(a))

   .. tab:: Data Spec

      .. code-block:: json

         {
           "users": {
             "type": "values",
             "data": ["bob", "bobby", "rob", "roberta", "steve", "flora", "fauna", "samantha", "abigail"],
             "config": {
               "count_dist": "gamma(a=3.4)",
               "sample": true,
               "as_list": true
             }
           }
         }

   .. tab:: Command and Output

      .. code-block:: shell

         $ datacraft -s spec.json -c dist.py -i 3 --log-level off
         ['abigail', 'flora', 'bob']
         ['rob', 'abigail']
         ['bobby', 'roberta', 'fauna', 'bob', 'rob', 'flora']

.. _casters:

Casting Values
^^^^^^^^^^^^^^

The CasterInterface exists to modify the results of generated data in small ways. An example would be the
``rand_range`` type that produces floating point numbers within a given range. If you want an integer in the range
provided by the supplier, you can use the ``"cast": "int"`` config param.  Below is a table of all of the built in
caster types. Custom casters can be registered with the ``@datacraft.registry.casters`` decorator as well.  See example
below.

Built in Casters
~~~~~~~~~~~~~~~~

.. table::
   :widths: 15 60 15 15

   +-------+------------------------------------------+--------+--------+
   | name  | description                              | input  | output |
   +=======+==========================================+========+========+
   | int   | casts floats or string floats to integers| 44.567 | 44     |
   +-------+------------------------------------------+--------+--------+
   | i     | alias for int                            |        |        |
   +-------+------------------------------------------+--------+--------+
   | float | casts float strings or integers to floats| 44     | 44.0   |
   +-------+------------------------------------------+--------+--------+
   |       |                                          | '44.23'| 44.23  |
   +-------+------------------------------------------+--------+--------+
   |       |                                          | '44.23'| 44.23  |
   +-------+------------------------------------------+--------+--------+
   | f     | alias for float                          |        |        |
   +-------+------------------------------------------+--------+--------+
   | string| casts any type to a string               | 123    | '123'  |
   +-------+------------------------------------------+--------+--------+
   |       |                                          | 44.23  | '44.23'|
   +-------+------------------------------------------+--------+--------+
   |       |                                          | True   | 'True' |
   +-------+------------------------------------------+--------+--------+
   | str   | alias for string                         |        |        |
   +-------+------------------------------------------+--------+--------+
   | s     | alias for string                         |        |        |
   +-------+------------------------------------------+--------+--------+
   | hex   | casts integer objects to hexidecimal form| 123    | '0x7b' |
   +-------+------------------------------------------+--------+--------+
   |       |                                          | 1023   | '0x3ff'|
   +-------+------------------------------------------+--------+--------+
   | h     | alias for hex                            |        |        |
   +-------+------------------------------------------+--------+--------+
   | lower | casts to string and lower cases value    | 'aBcD' | 'abcd' |
   +-------+------------------------------------------+--------+--------+
   |       |                                          | 123    | '123'  |
   +-------+------------------------------------------+--------+--------+
   |       |                                          | True   | 'true' |
   +-------+------------------------------------------+--------+--------+
   | l     | alias for lower                          |        |        |
   +-------+------------------------------------------+--------+--------+
   | upper | casts to string and upper cases value    | 'aBcD' | 'ABCD' |
   +-------+------------------------------------------+--------+--------+
   |       |                                          | 123    | '123'  |
   +-------+------------------------------------------+--------+--------+
   |       |                                          | True   | 'TRUE' |
   +-------+------------------------------------------+--------+--------+
   | u     | alias for upper                          |        |        |
   +-------+------------------------------------------+--------+--------+
   | trim  | removes leading and trailing whitespace  | ' val '| 'val'  |
   +-------+------------------------------------------+--------+--------+
   | t     | alias for trim                           |        |        |
   +-------+------------------------------------------+--------+--------+
   | round | round to nearest integer                 | 44.567 | 45     |
   +-------+------------------------------------------+--------+--------+
   |       |                                          | 44.123 | 44     |
   +-------+------------------------------------------+--------+--------+
   | round0| round to ones, type is float             | 44.567 | 45.0   |
   +-------+------------------------------------------+--------+--------+
   | round1| round to first decimal place             | 44.567 | 45.6   |
   +-------+------------------------------------------+--------+--------+
   |       |                                          | 44.123 | 44.1   |
   +-------+------------------------------------------+--------+--------+
   | round2| round to second decimal place            | 44.567 | 45.57  |
   +-------+------------------------------------------+--------+--------+
   |       |                                          | 44.123 | 44.12  |
   +-------+------------------------------------------+--------+--------+
   | ...   | same for round3 up to round9             |        |        |
   +-------+------------------------------------------+--------+--------+
   | zfill1| zero fill to one character               | 1      | 1      |
   +-------+------------------------------------------+--------+--------+
   |       |                                          | ''     | 0      |
   +-------+------------------------------------------+--------+--------+
   | zfill2| zero fill to two characters              | 1      | 01     |
   +-------+------------------------------------------+--------+--------+
   |       |                                          | 22     | 22     |
   +-------+------------------------------------------+--------+--------+
   | zfill3| zero fill to three characters            | c      | 00c    |
   +-------+------------------------------------------+--------+--------+
   |       |                # 4 characters -> no fill | 44.1   | 44.1   |
   +-------+------------------------------------------+--------+--------+
   | ...   | same for up to zfill10                   |        |        |
   +-------+------------------------------------------+--------+--------+

.. _custom_value_casters:

Custom Value Casters
^^^^^^^^^^^^^^^^^^^^

Custom casters can be supplied using :ref:`custom code<custom_code>` loading and the
``@datacraft.registry.casters`` decorator:

.. tabs::

   .. tab:: Custom Code

      .. code-block:: python

         from typeing import Any
         import datacraft

         class _ReverseCaster(datacraft.CasterInterface):
             def cast(self, value: Any) -> str:
                 return str(value)[::-1]

         @datacraft.registry.casters('reverse')
         def _reverse_caster() -> datacraft.CasterInterface:
             """ example custom caster """
             return _ReverseCaster()

   .. tab:: Data Spec

      .. code-block:: json

         {
           "cast_demo": {
             "type": "values",
             "data": ["zebra", "llama", "donkey", "flamingo", "rhinoceros"],
             "config": {
               "cast": "reverse"
             }
           }
         }

   .. tab:: Command and Output

      .. code-block:: shell

         $ datacraft -s cast.json -c cast.py -i 5  --log-level off
         arbez
         amall
         yeknod
         ognimalf
         soreconihr

