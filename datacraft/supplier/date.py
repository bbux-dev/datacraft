"""
Module for date type implementations
"""
import datetime

from .model import ValueSupplierInterface, Distribution


def date_supplier(date_format: str,
                  timestamp_distribution: Distribution,
                  hour_supplier: ValueSupplierInterface = None) -> ValueSupplierInterface:
    """
    Creates a value supplier that provides dates with the given format

    Args:
        date_format: format string for dates
        timestamp_distribution: distribution object that will provide the timestamps that will be formatted
        hour_supplier: supplier for hours to set on each generated date, to restrict dates to certain time periods

    Returns:
        ValueSupplierInterface that supplies dates with the given format
    """
    return _DateSupplier(timestamp_distribution, date_format, hour_supplier)


class _DateSupplier(ValueSupplierInterface):
    """
    Value Supplier implementation for dates
    """

    def __init__(self,
                 timestamp_distribution: Distribution,
                 date_format_string: str,
                 hour_supplier: ValueSupplierInterface = None):
        """
        Args:
            timestamp_distribution: distribution for timestamps
            date_format_string: format string for timestamps
            hour_supplier: supplier for hours to set on each generated date, to restrict dates to certain time periods
        """
        self.date_format = date_format_string
        self.timestamp_distribution = timestamp_distribution
        self.hour_supplier = hour_supplier

    def next(self, iteration):
        random_seconds = self.timestamp_distribution.next_value()
        next_date = datetime.datetime.fromtimestamp(random_seconds)
        if self.hour_supplier:
            next_hour = self.hour_supplier.next(iteration)
            next_date = next_date.replace(hour=int(next_hour))
        if self.date_format:
            return next_date.strftime(self.date_format)
        return next_date.replace(microsecond=0).isoformat()
