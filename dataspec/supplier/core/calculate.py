""" module for handling calculate types """
import json
import dataspec
import keyword


class CalculateSupplier(dataspec.ValueSupplierInterface):
    """
    ValueSupplier for calculate types

    Applies evaluation of simple formulas from the results of other suppliers

    i.e:

    height_ft = [5, 6, 7]
    height_cm = [ft * 30.48 for ft in height_ft]

    Takes dictionary of alias -> supplier and a formula

    Formula should contain operations for values returned by aliases suppliers

    i.e.:

    >>> formula = "ft * 30.48"
    >>> suppliers = { "ft": 'a': dataspec.suppliers.values([4, 5, 6]) }
    >>> calculate = CalculateSupplier(suppliers=suppliers, formula=formula)
    >>> asssert calculate.next(0) ==
    """

    def __init__(self, suppliers: dict, formula: str):
        self.suppliers = suppliers
        self.formula = formula

    def next(self, iteration):
        for alias, supplier in self.suppliers.items():
            exec(f'{alias} = {supplier.next(iteration)}')
        return eval(self.formula)


@dataspec.registry.schemas('calculate')
def get_combine_list_schema():
    """ get the schema for the calculate type """
    return dataspec.schemas.load('calculate')


@dataspec.registry.types('calculate')
def configure_calculate_supplier(field_spec: dict, loader: dataspec.Loader):
    """ configures supplier for calculate type """
    if 'refs' not in field_spec and 'fields' not in field_spec:
        raise dataspec.SpecException('Must define one of fields or refs. %s' % json.dumps(field_spec))
    if 'refs' in field_spec and 'fields' in field_spec:
        raise dataspec.SpecException('Must define only one of fields or refs. %s' % json.dumps(field_spec))
    if 'formula' not in field_spec:
        raise dataspec.SpecException('Must define formula for calculate type. %s' % json.dumps(field_spec))

    key = 'refs' if 'refs' in field_spec else 'fields'
    mappings = field_spec[key]
    if len(mappings) < 1 or not isinstance(mappings, dict):
        raise dataspec.SpecException('mapping pointer must be dictionary. %s' % json.dumps(field_spec))

    suppliers = {}
    for ref, alias in mappings.items():
        if keyword.iskeyword(alias):
            raise dataspec.SpecException(
                'Invalid alias for calculate spec: %s is a keyword, try _%s instead', alias, alias)
        supplier = loader.get(ref)
        suppliers[alias] = supplier

    return CalculateSupplier(suppliers=suppliers, formula=field_spec.get('formula'))
