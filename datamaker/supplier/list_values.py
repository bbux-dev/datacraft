class ListValueSupplier:
    def __init__(self, data):
        self.values = data

    def next(self, iteration):
        idx = iteration % len(self.values)
        data = self.values[idx]
        return data
