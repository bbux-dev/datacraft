"""
Module for calculate type implementations
"""
from typing import Dict

import asteval  # type: ignore

from .model import ValueSupplierInterface, RecordProcessor


def calculate_supplier(suppliers: Dict[str, ValueSupplierInterface], engine: RecordProcessor) -> ValueSupplierInterface:
    """
    Creates a calculate supplier that will perform the calculation on the formula interpreted by the given engine.

    Applies evaluation of simple formulas from the results of other suppliers

    i.e:

    height_ft = [5, 6, 7]

    height_cm = [ft * 30.48 for ft in height_ft]

    Takes dictionary of alias -> supplier and a formula

    Formula should contain operations for values returned by aliases suppliers

    Variables should be encased in Jinja2 double brace format

    Args:
        suppliers: map of field/alias to supplier of values for that field/alias
        engine: interpolate the field values with

    Returns:
        ValueSupplierInterface that performs the calculation for each iteration

    Examples:
        >>> import datacraft
        >>> formula = "{{ft}} * 30.48"
        >>> ft_supplier = { "ft": ft_supplier.values([4, 5, 6]) }
        >>> calculate = _CalculateSupplier(suppliers=ft_supplier, formula=formula)
        >>> assert calculate.next(0) == 121.92
    """
    return _CalculateSupplier(suppliers, engine)


class _CalculateSupplier(ValueSupplierInterface):
    """
    ValueSupplier for calculate types
    """

    def __init__(self, suppliers: dict, engine: RecordProcessor):
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
