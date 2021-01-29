"""
Module for implementation of select list subset value supplier
"""
import math
import random
import sys
from random import gauss

from dataspec.supplier.value_supplier import ValueSupplierInterface


class SelectListSupplier(ValueSupplierInterface):
    """
    Implementation for supplying values from a list by select a portion of them and joining them by some delimiter
    """

    def __init__(self, data, config):
        self.values = data
        self.mean = float(config.get('mean'))
        self.stddev = config.get('stddev', 0)
        self.min = int(config.get('min', 1))
        self.max = int(config.get('max', sys.maxsize))
        self.join_with = config.get('join_with', ' ')

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
        return self.join_with.join(data)
