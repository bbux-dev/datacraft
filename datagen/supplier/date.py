"""
Module for date type implementations
"""
import datetime

from .model import ValueSupplierInterface, Distribution


def date_supplier(date_format, timestamp_distribution):
    return _DateSupplier(timestamp_distribution, date_format)


class _DateSupplier(ValueSupplierInterface):
    """
    Value Supplier implementation for dates
    """

    def __init__(self,
                 timestamp_distribution: Distribution,
                 date_format_string: str):
        """
        Args:
            timestamp_distribution: distribution for timestamps
            date_format_string: format string for timestamps
        """

        self.date_format = date_format_string
        self.timestamp_distribution = timestamp_distribution

    def next(self, iteration):
        random_seconds = self.timestamp_distribution.next_value()
        next_date = datetime.datetime.fromtimestamp(random_seconds)
        if self.date_format:
            return next_date.strftime(self.date_format)
        return next_date.replace(microsecond=0).isoformat()