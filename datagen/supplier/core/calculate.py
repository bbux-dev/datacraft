"""
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

.. code-block:: json

    {
      "height_in": [60, 70, 80, 90],
      "height_cm": {
        "type": "calculate",
        "fields": ["height_in"],
        "formula": "{{ height_in }} * 2.54"
      }
    }

.. code-block:: json

    {
      "long_name_one": {
        "type": "values",
        "data": [4, 5, 6]
      },
      "long_name_two": {
        "type": "values",
        "data": [3, 6, 9]
      },
      "c": {
        "type": "calculate",
        "fields": {
          "long_name_one": "a",
          "long_name_two": "b"
        },
        "formula": "sqrt({{a}}*{{a}} + {{b}}*{{b}})"
      }
    }

We use the `asteval <http://newville.github.io/asteval/basics.html>`_
package to do formula evaluation. This provides a fairly safe way to do
evaluation. The package provides a bunch of
`built-in-functions <http://newville.github.io/asteval/basics.html#built-in-functions>`_
as well. We also use the `Jinja2 <https://pypi.org/project/Jinja2/>`_ templating
engine format for specifying variable names to substitute. In theory, you
could use any valid jinja2 syntax i.e.:

.. code-block:: json

    {
      "formula": "sqrt({{ value_that_might_be_a_string | int }})"
    }

"""
import json
import keyword
import logging
import asteval  # type: ignore
import datagen

log = logging.getLogger(__name__)


class CalculateSupplier(datagen.ValueSupplierInterface):
    """
    ValueSupplier for calculate types

    Applies evaluation of simple formulas from the results of other suppliers

    i.e:

    height_ft = [5, 6, 7]

    height_cm = [ft * 30.48 for ft in height_ft]

    Takes dictionary of alias -> supplier and a formula

    Formula should contain operations for values returned by aliases suppliers

    Variables should be encased in Jinja2 double brace format

    Examples:
        >>> import datagen
        >>> formula = "{{ft}} * 30.48"
        >>> suppliers = { "ft": datagen.suppliers.values([4, 5, 6]) }
        >>> calculate = CalculateSupplier(suppliers=suppliers, formula=formula)
        >>> asssert calculate.next(0) == 121.92
    """

    def __init__(self, suppliers: dict, engine: datagen.model.RecordProcessor):
        self.suppliers = suppliers
        self.engine = engine
        self.aeval = asteval.Interpreter()

    def next(self, iteration):
        # make a copy to manipulate
        values = {}
        for alias, supplier in self.suppliers.items():
            values[alias] = supplier.next(iteration)
        formula = self.engine.process(values)
        return self.aeval(formula)


@datagen.registry.schemas('calculate')
def _calculate_schema():
    """ get the schema for the calculate type """
    return datagen.schemas.load('calculate')


@datagen.registry.types('calculate')
def _configure_calculate_supplier(field_spec: dict, loader: datagen.Loader):
    """ configures supplier for calculate type """
    if 'refs' not in field_spec and 'fields' not in field_spec:
        raise datagen.SpecException('Must define one of fields or refs. %s' % json.dumps(field_spec))
    if 'refs' in field_spec and 'fields' in field_spec:
        raise datagen.SpecException('Must define only one of fields or refs. %s' % json.dumps(field_spec))
    template = field_spec.get('formula')
    if template is None:
        raise datagen.SpecException('Must define formula for calculate type. %s' % json.dumps(field_spec))

    mappings = _get_mappings(field_spec, 'refs')
    mappings.update(_get_mappings(field_spec, 'fields'))

    if len(mappings) < 1:
        raise datagen.SpecException('fields or refs empty: %s' % json.dumps(field_spec))

    suppliers = {}
    for field_or_ref, alias in mappings.items():
        supplier = loader.get(field_or_ref)
        suppliers[alias] = supplier

    engine = datagen.template_engines.string(template)
    return CalculateSupplier(suppliers=suppliers, engine=engine)


def _get_mappings(field_spec, key):
    """ retrieve the field aliasing for the given key, refs or fields """
    mappings = field_spec.get(key, [])
    if isinstance(mappings, list):
        mappings = {key: key for key in mappings}
    return mappings
