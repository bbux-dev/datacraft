import random


class ListValueSupplier:
    def __init__(self, data, do_sampling=False):
        self.values = data
        self.do_sampling = do_sampling

    def next(self, iteration):
        if self.do_sampling:
            return random.sample(self.values, 1)[0]
        else:
            idx = iteration % len(self.values)
            return self.values[idx]
