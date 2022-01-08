"""Implementation for templated supplier"""
from typing import Dict


from .model import ValueSupplierInterface, RecordProcessor


class _TemplateValueSupplier(ValueSupplierInterface):

    def __init__(self,
                 supplier_map: Dict[str, ValueSupplierInterface],
                 engine: RecordProcessor):
        self.suppliers = supplier_map
        self.engine = engine

    def next(self, iteration):
        data = {key: val.next(iteration) for key, val in self.suppliers.items()}
        return self.engine.process(data)


def templated_supplier(supplier_map: Dict[str, ValueSupplierInterface],
                       engine: RecordProcessor) -> ValueSupplierInterface:
    """
    Creates a supplier that populates the template string from the supplier map

    Args:
        supplier_map: map of field name -> value supplier for it
        engine: for processing templated string

    Returns:
        value supplier for template
    """
    return _TemplateValueSupplier(supplier_map, engine)
