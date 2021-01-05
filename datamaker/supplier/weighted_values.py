import random

class WeightedValueSupplier(object):
    def __init__(self, spec):
        data = spec.get('data')
        self.choices = list(data.keys())
        self.weights = data.values()

    def next(self, iteration):
        return random.choices(self.choices, self.weights)[0]
