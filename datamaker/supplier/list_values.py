class ListValueSupplier(object):
    def __init__(self, spec):
        self.values = spec.get('data')

    def next(self, iteration):
        idx = iteration % len(self.values)
        data = self.values[idx]
        return data
