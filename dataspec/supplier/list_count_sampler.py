""" Module for ListCountSamplerSupplier """
import random

from dataspec.supplier.value_supplier import ValueSupplierInterface


class ListCountSamplerSupplier(ValueSupplierInterface):
    """
    Supplies values by sampling from a list with hard min max and count
    """

    def __init__(self, data: list, count_supplier: ValueSupplierInterface, join_with: bool = None):
        self.values = data
        self.count_supplier = count_supplier
        self.join_with = join_with

    def next(self, iteration):
        count = self.count_supplier.next(iteration)
        data = random.sample(self.values, count)
        if self.join_with:
            return self.join_with.join([str(elem) for elem in data])
        return data
