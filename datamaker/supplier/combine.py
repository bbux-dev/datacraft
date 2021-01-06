class CombineValuesSupplier:
    def __init__(self, suppliers, config=None):
        self.suppliers = suppliers
        self.config = config

    def next(self, iteration):
        values = [str(supplier.next(iteration)) for supplier in self.suppliers]
        if self.config and 'join_with' in self.config:
            joiner = self.config.get('join_with')
        else:
            joiner = ''
        return joiner.join(values)
