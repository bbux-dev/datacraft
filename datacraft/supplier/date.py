"""
Module for date type implementations
"""
import datetime
import logging
from typing import Union, Tuple

from .model import ValueSupplierInterface, Distribution

_log = logging.getLogger(__name__)


def date_supplier(date_format: str,
                  timestamp_distribution: Distribution,
                  hour_supplier: Union[ValueSupplierInterface, None] = None) -> ValueSupplierInterface:
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


def epoch_date_supplier(timestamp_distribution: Distribution,
                        is_millis: bool = False) -> ValueSupplierInterface:
    """
    Creates a value supplier that provides dates with the given format

    Args:
        timestamp_distribution: distribution object that will provide the timestamps that will be formatted
        is_millis: should this be a millisecond based timestamp

    Returns:
        ValueSupplierInterface that supplies dates with the given format
    """
    return _EpochDateSupplier(timestamp_distribution, is_millis)


class _DateSupplier(ValueSupplierInterface):
    """
    Value Supplier implementation for dates
    """

    def __init__(self,
                 timestamp_distribution: Distribution,
                 date_format_string: str,
                 hour_supplier: Union[ValueSupplierInterface, None] = None):
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


class _EpochDateSupplier(ValueSupplierInterface):
    """
    Value Supplier implementation for epoch dates
    """

    def __init__(self,
                 timestamp_distribution: Distribution,
                 is_millis: bool = False):
        """
        Args:
            timestamp_distribution: distribution for timestamps
            is_millis: should this be a millisecond based timestamp
        """
        self.timestamp_distribution = timestamp_distribution
        self.is_millis = is_millis

    def next(self, iteration):
        random_seconds = self.timestamp_distribution.next_value()
        if self.is_millis:
            return int(random_seconds*1000)
        return int(random_seconds)


def uniform_date_timestamp(
        start: str,
        end: str,
        offset: int,
        duration: int,
        date_format_string: str) -> Union[Tuple[None, None], Tuple[int, int]]:
    """
    Creates a uniform distribution for the start and end dates shifted by the offset

    Args:
        start: start date string
        end: end date string
        offset: number of days to shift the duration, positive is back negative is forward
        duration: number of days after start
        date_format_string: format for parsing dates

    Returns:
        Distribution that gives uniform seconds since epoch for the given params
    """
    offset_date = datetime.timedelta(days=offset)
    if start:
        try:
            start_date = datetime.datetime.strptime(start, date_format_string) - offset_date
        except TypeError as err:
            raise ValueError(f"TypeError. Format: {date_format_string}, may not match param: {start}") from err
    else:
        start_date = datetime.datetime.now() - offset_date
    if end:
        # buffer end date by one to keep inclusive
        try:
            end_date = datetime.datetime.strptime(end, date_format_string) \
                + datetime.timedelta(days=1) - offset_date
        except TypeError as err:
            raise ValueError(f"TypeError. Format: {date_format_string}, may not match param: {end}") from err
    else:
        # start date already include offset, don't include it here
        end_date = start_date + datetime.timedelta(days=abs(int(duration)), seconds=1)

    start_ts = int(start_date.timestamp())
    end_ts = int(end_date.timestamp())
    if end_ts < start_ts:
        _log.warning("End date (%s) is before start date (%s)", start_date, end_date)
        return None, None
    return start_ts, end_ts
