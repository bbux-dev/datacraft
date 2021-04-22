"""
Module holds the Interface that Value Suppliers should implement.
"""


class ValueSupplierInterface:
    """
    Interface for Classes that supply values
    """
    def next(self, iteration):
        """
        Produces the next value for the given iteration
        :param iteration: current iteration
        :return: the next value
        """
