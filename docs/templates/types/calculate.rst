{%- from "macros.jinja" import show_example with context %}
calculate
---------

There are times when one field needs the value of another field in order to
calculate its own value. For example, if you wanted to produce values that
represented a users' height in inches and in centimeters, you would want them to
correlate. You could use the `calculate` type to specify a `formula` to do this
calculation. There are two ways to specify the fields to calculate a value from.
The first is to use the `fields` and/or the `refs` keys with an array of fields
or refs to use in the formula.  The second is the use a map where the field
or ref name to be used is mapped to a string that will be used as an alias for
it in the formula. See second example below for the mapped alias version.

Prototype:

.. code-block:: python

    {
      "<field name>": {
        "type": "calculate",
        "fields": List[str],
        or
        "refs": List[str],
        "formula": <formula>
        "config": {
          "key": Any
        }
      }
    }

    formula (str): The formula to use in calculations

Examples:

{{ show_example(examples.calculate_1) }}

{{ show_example(examples.calculate_2) }}



We use the `asteval <http://newville.github.io/asteval/basics.html>`_
package to do formula evaluation. This provides a fairly safe way to do
evaluation. The package provides a bunch of
`built-in-functions <http://newville.github.io/asteval/basics.html#built-in-functions>`_
as well. We also use the `Jinja2 <https://pypi.org/project/Jinja2/>`_ templating
engine format for specifying variable names to substitute. In theory, you
could use any valid jinja2 syntax i.e.:

{% raw %}
.. code-block:: json

    {
      "formula": "sqrt({{ value_that_might_be_a_string | int }})"
    }
{% endraw -%}