"""
module for handling calculate types
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

    i.e.:

    Examples:
        >>> import datagen
        >>> formula = "ft * 30.48"
        >>> suppliers = { "ft": datagen.suppliers.values([4, 5, 6]) }
        >>> calculate = CalculateSupplier(suppliers=suppliers, formula=formula)
        >>> asssert calculate.next(0) == 121.92
    """

    def __init__(self, suppliers: dict, engine: datagen.template_engines.Jinja2Engine):
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
    if field_spec.get('formula') is None:
        raise datagen.SpecException('Must define formula for calculate type. %s' % json.dumps(field_spec))

    mappings = _get_mappings(field_spec, 'refs')
    mappings.update(_get_mappings(field_spec, 'fields'))

    if len(mappings) < 1:
        raise datagen.SpecException('fields or refs empty: %s' % json.dumps(field_spec))

    suppliers = {}
    for field_or_ref, alias in mappings.items():
        supplier = loader.get(field_or_ref)
        suppliers[alias] = supplier

    template = field_spec.get('formula')
    engine = datagen.template_engines.string(template)
    return CalculateSupplier(suppliers=suppliers, engine=engine)


def _get_mappings(field_spec, key):
    """ retrieve the field aliasing for the given key, refs or fields """
    mappings = field_spec.get(key, [])
    if isinstance(mappings, list):
        mappings = {key: key for key in mappings}
    return mappings
