import random

class WeightedValueSupplier(object):
    def __init__(self, data):
        # may be passed raw data or a spec
        if isinstance(data, dict) and 'data' in data:
            data = data.get('data')
        self.choices = list(data.keys())
        self.weights = data.values()

    def next(self, iteration):
        return random.choices(self.choices, self.weights)[0]
