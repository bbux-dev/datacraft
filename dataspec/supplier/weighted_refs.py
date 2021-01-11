from dataspec.exceptions import SpecException


class WeightedRefsSupplier:
    def __init__(self, key_supplier, values_map):
        self.key_supplier = key_supplier
        self.values_map = values_map

    def next(self, iteration):
        key = self.key_supplier.next(iteration)
        supplier = self.values_map.get(key)
        if supplier is None:
            raise SpecException("Unknown Key '%s' for Weighted Reference" % key)
        return supplier.next(iteration)
