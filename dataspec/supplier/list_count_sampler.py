""" Module for ListCountSamplerSupplier """
import random

from dataspec.supplier.value_supplier import ValueSupplierInterface


class ListCountSamplerSupplier(ValueSupplierInterface):
    """
    Supplies values by sampling from a list with hard min max and count
    """

    def __init__(self, data, config):
        self.values = data

        count = config.get('count')
        if count is not None:
            self.count_range = [int(count)]
        else:
            min_cnt = int(config.get('min', 1))
            max_cnt = int(config.get('max', len(self.values))) + 1
            self.count_range = list(range(min_cnt, max_cnt))
        self.join_with = config.get('join_with', None)

    def next(self, _):
        count = random.sample(self.count_range, 1)[0]
        if count <= 0:
            count = 1

        data = random.sample(self.values, count)
        if self.join_with:
            return self.join_with.join([str(elem) for elem in data])
        return data
