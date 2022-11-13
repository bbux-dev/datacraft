"""
Module for numeric distributions such as uniform or gaussian
"""
from typing import Union
import random
import inspect
import logging

from . import registries
from .supplier.model import Distribution

_log = logging.getLogger(__name__)


class UniformDistribution(Distribution):
    """Class that samples values from a uniform distribution between the start and end points """

    def __init__(self, start: float, end: float):
        """
        Args:
            start: of range
            end: end or range
        """
        self.start = start
        self.end = end

    def next_value(self):
        return random.uniform(self.start, self.end)


class GaussDistribution(Distribution):
    """Class that samples values from a normal distribution with provided mean and standard deviation """

    def __init__(self, mean: float, stddev: float):
        """
        Args:
            mean: of range
            stddev: of range
        """
        self.mean = mean
        self.stddev = stddev

    def next_value(self):
        return random.gauss(self.mean, self.stddev)


class BoundedDistribution(Distribution):
    """Class bounds another distribution """

    def __init__(self,
                 distribution: Distribution,
                 min_val: float = 0.0,
                 max_val: Union[float, None] = None):
        """
        Args:
            distribution: to bound
            min_val: min value to return
            max_val: max value to return
        """
        self.distribution = distribution
        self.min = min_val
        self.max = max_val

    def next_value(self):
        value = self.distribution.next_value()
        if self.min and value < self.min:
            return self.min
        if self.max and value > self.max:
            return self.max
        return value


@registries.Registry.distribution('uniform')
def uniform(start, end):
    """ uniform distribution for from start to end """
    return UniformDistribution(start, end)


@registries.Registry.distribution('normal')
def normal(mean, stddev, **kwargs):
    """ normal distribution for normal keyword """
    return _gaussian_distribution(mean, stddev, **kwargs)


@registries.Registry.distribution('gauss')
def gauss(mean, stddev, **kwargs):
    """ normal distribution for gauss keyword """
    return _gaussian_distribution(mean, stddev, **kwargs)


@registries.Registry.distribution('gaussian')
def gaussian(mean, stddev, **kwargs):
    """ normal distribution for gaussian keyword """
    return _gaussian_distribution(mean, stddev, **kwargs)


def _gaussian_distribution(mean, stddev, **kwargs):
    """ normal distribution for mean and standard deviation """
    distribution = GaussDistribution(mean, stddev)
    if 'min' in kwargs or 'max' in kwargs:
        return BoundedDistribution(distribution, kwargs.get('min'), kwargs.get('max'))
    return distribution


def from_string(dist_func_str: str) -> Distribution:
    """
    Uses a function form of the distribution to look up and configure it

    Distribution params need to use key=value format

    Args:
        dist_func_str: that specifies the distribution along with its args

    Returns:
        the specified distribution if registered

    Examples:
        >>> import datacraft
        >>> distribution = datacraft.distributions.from_string("uniform(start=10, end=25)")
        >>> distribution.next_value()
        22.87795012038216
    """
    try:
        open_paren = dist_func_str.index('(')
        close_paren = dist_func_str.index(')')
    except ValueError as value_error:
        raise ValueError('Invalid function format: ' + dist_func_str) from value_error

    if open_paren == 0 or close_paren < open_paren or close_paren != len(dist_func_str.strip()) - 1:
        raise ValueError('Invalid function format: ' + dist_func_str)

    name = dist_func_str[0:open_paren]
    dist_func = registries.Registry.distribution.get(name)

    args = dist_func_str[open_paren + 1:close_paren]
    kwargs = _convert_to_kwargs(args)

    if kwargs is None or _invalid_args_for_func(dist_func, kwargs):
        raise ValueError('Invalid args for function: ' + dist_func_str)

    return dist_func(**kwargs)


def _invalid_args_for_func(dist_func, kwargs):
    """ verifies the args match """
    argspec = inspect.getfullargspec(dist_func)
    expected_args = argspec.args
    actual_args = list(set(kwargs.keys()) - {'min', 'max'})
    if sorted(actual_args) != sorted(expected_args):
        _log.warning('expected args: %s, actual: %s', expected_args, actual_args)
        return True
    # args are not invalid
    return False


def _convert_to_kwargs(args: str) -> Union[dict, None]:
    """
    converts string of key=val, ..., key=val to dictionary

    Args:
        args: to convert

    Returns:
        dictionary of key values
    """
    parts = args.split(',')
    kwargs = {}
    for part in parts:
        keyval = part.split('=')
        if len(keyval) != 2:
            return None
        kwargs[keyval[0].strip()] = float(keyval[1].strip())
    return kwargs
