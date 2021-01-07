"""
Supplies values by selecting and joining elements from a list
"""
import math
import random
from random import gauss


class SelectListSupplier:
    def __init__(self, data, config):
        self.values = data
        self.mean = config.get('mean')
        self.stddev = config.get('stddev', 0)
        self.min = int(config.get('min'))
        self.max = int(config.get('max'))
        self.join_with = config.get('join_with', ' ')

    def next(self, iteration):
        count = math.ceil(gauss(self.mean, self.stddev))
        if count <= 0:
            count = 1
        if count > self.max:
            count = self.max
        if count < self.min:
            count = self.min
        # last check, cant sample more than exists
        if count > len(self.values):
            count = len(self.values)

        data = random.sample(self.values, count)
        return self.join_with.join(data)
