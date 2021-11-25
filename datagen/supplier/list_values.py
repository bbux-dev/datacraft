"""
Module for value list supplier implementation
"""
import random

import datagen


class ListValueSupplier(datagen.ValueSupplierInterface):
    """
    Value Supplier implementation for supplying values from lists
    """

    def __init__(self,
                 data: list,
                 count_supplier: datagen.ValueSupplierInterface,
                 do_sampling: bool = False,
                 as_list: bool = False):
        """
        Args:
            data: to rotate through
            count_supplier: to supply number of values to return
            do_sampling: if the list should be sampled from, default is to rotate through in order
            as_list: if results should be returned as a list
        """
        self.values = data
        self.do_sampling = do_sampling
        self.count = count_supplier
        self.as_list = as_list

    def next(self, iteration):
        cnt = self.count.next(iteration)
        if self.do_sampling:
            values = random.sample(self.values, cnt)
        else:
            values = [self._value(iteration, i) for i in range(cnt)]
        if cnt == 1 and not self.as_list:
            return values[0]
        return values

    def _value(self, iteration, i):
        idx = (iteration + i) % len(self.values)
        return self.values[idx]
