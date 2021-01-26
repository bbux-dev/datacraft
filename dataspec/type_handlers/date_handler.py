import random
import datetime
import dataspec

DEFAULT_FORMAT = "%d-%m-%Y"
ISO_FORMAT_NO_MICRO = '%Y-%m-%dT%H:%M:%S'
ISO_FORMAT_WITH_MICRO = '%Y-%m-%dT%H:%M:%S.%f'


class DateSupplier:
    def __init__(self, delta_days, offset, anchor, date_format_string):
        self.date_format = date_format_string

        offset_date = datetime.timedelta(days=offset)
        if anchor:
            base = datetime.datetime.strptime(anchor, date_format_string) - offset_date
        else:
            base = datetime.datetime.now() - offset_date

        self.start_date, end_date = _calculate_start_end_dates(base, delta_days)
        self.delta_seconds = _calculate_delta_seconds(self.start_date, end_date)

    def next(self, _):
        random_second = random.randrange(self.delta_seconds)
        next_date = self.start_date + datetime.timedelta(seconds=random_second)
        if self.date_format:
            return next_date.strftime(self.date_format)
        return next_date.replace(microsecond=0).isoformat()


@dataspec.registry.types('date')
def configure_supplier(field_spec, _):
    config = field_spec.get('config', {})
    delta_days = config.get('delta_days', 15)
    offset = int(config.get('offset', 0))
    anchor = config.get('anchor')
    date_format = config.get('format', DEFAULT_FORMAT)
    return DateSupplier(delta_days, offset, anchor, date_format)


@dataspec.registry.types('date.iso')
def configure_supplier_iso(field_spec, _):
    return _configure_supplier_iso_date(field_spec, ISO_FORMAT_NO_MICRO)


@dataspec.registry.types('date.iso.us')
def configure_supplier_iso_microseconds(field_spec, _):
    return _configure_supplier_iso_date(field_spec, ISO_FORMAT_WITH_MICRO)


def _configure_supplier_iso_date(field_spec, iso_date_format):
    config = field_spec.get('config', {})
    delta_days = config.get('delta_days', 15)
    offset = int(config.get('offset', 0))
    anchor = config.get('anchor')
    date_format = config.get('format', DEFAULT_FORMAT)
    # make sure the anchor matches the ISO format we are using
    if anchor:
        anchor_date = datetime.datetime.strptime(anchor, date_format)
        anchor = anchor_date.strftime(iso_date_format)
    return DateSupplier(delta_days, offset, anchor, iso_date_format)


def _calculate_start_end_dates(base, delta_days):
    """
    Calculates the datetime objects for the start of delta_days ago and the start of delta_days+1 ahead
    To guarantee that the desired date range strings are created
    :param base:
    :param delta_days:
    :return:
    """
    lower, upper = _calculate_upper_lower(delta_days)
    start_date = (base + datetime.timedelta(days=lower)).replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = (base + datetime.timedelta(days=upper)).replace(hour=0, minute=0, second=0, microsecond=0)
    return start_date, end_date


def _calculate_upper_lower(delta_days):
    """
    Calculates the lower and upper bounds based on the many formats accepted by delta days
    :param delta_days:
    :return: the lower and upper number of days for delta
    """
    if isinstance(delta_days, list):
        lower = int(delta_days[0])
        upper = int(delta_days[1])
    else:
        lower = -int(delta_days)
        upper = int(delta_days)
    lower = -(abs(lower))
    # this makes end date inclusive
    upper = abs(upper) + 1
    return lower, upper


def _calculate_delta_seconds(start, end):
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    return int_delta
