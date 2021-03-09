"""
Module for implementation of select list subset value supplier
"""
import math
import random
from random import gauss
from dataspec.utils import is_affirmative
from dataspec.supplier.value_supplier import ValueSupplierInterface


class ListSampler(ValueSupplierInterface):
    """
    Implementation for supplying values from a list by select a portion of them
    and optionally joining them by some delimiter
    """

    def __init__(self, data, config):
        self.values = data
        self.mean = float(config.get('mean'))
        self.stddev = config.get('stddev', 0)
        self.min = int(config.get('min', 1))
        self.max = int(config.get('max', len(self.values)))
        self.join_with = config.get('join_with', ' ')
        self.as_list = is_affirmative('as_list', config, False)

    def next(self, _):
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
        if self.as_list:
            return data
        return self.join_with.join(data)
