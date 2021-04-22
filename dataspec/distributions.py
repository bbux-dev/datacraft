"""
Module for numeric distributions such as uniform or gaussian
"""
import random
import inspect
import dataspec
from dataspec.model import Distribution


class UniformDistribution(Distribution):
    """
    Class that samples values from a uniform distribution between the start and end points
    """

    def __init__(self, start: float, end: float) -> Distribution:
        self.start = start
        self.end = end

    def next_value(self):
        return random.uniform(self.start, self.end)


class GaussDistribution(Distribution):
    """
    Class the samples values from a normal distribution with provided mean and standard deviation
    """

    def __init__(self, mean: float, stddev: float) -> Distribution:
        self.mean = mean
        self.stddev = stddev

    def next_value(self):
        return random.gauss(self.mean, self.stddev)


@dataspec.registry.distribution('uniform')
def uniform(start, end):
    """ uniform distribution for from start to end """
    return UniformDistribution(start, end)


@dataspec.registry.distribution('normal')
def normal(mean, stddev):
    return _gaussian_distribution(mean, stddev)


@dataspec.registry.distribution('gauss')
def gauss(mean, stddev):
    return _gaussian_distribution(mean, stddev)


@dataspec.registry.distribution('gaussian')
def gaussian(mean, stddev):
    return _gaussian_distribution(mean, stddev)


def _gaussian_distribution(mean, stddev):
    return GaussDistribution(mean, stddev)


def from_string(dist_func_str: str) -> Distribution:
    """
    Uses a function form of the distribution to look up and configure it

    >>> distribution = dataspec.distributions.from_string("uniform(start=10, end=25)")

    Distribution params need to use key=value format
    :param dist_func_str:
    :return: the specified distribution if registered
    """
    try:
        open_paren = dist_func_str.index('(')
        close_paren = dist_func_str.index(')')
    except ValueError as value_error:
        raise ValueError('Invalid function format: ' + dist_func_str) from value_error

    if open_paren == 0 or close_paren < open_paren or close_paren != len(dist_func_str.strip()) - 1:
        raise ValueError('Invalid function format: ' + dist_func_str)

    name = dist_func_str[0:open_paren]
    dist_func = dataspec.registry.distribution.get(name)
    # for check what the names of the expected args are
    argspec = inspect.getfullargspec(dist_func)

    args = dist_func_str[open_paren + 1:close_paren]

    kwargs = _convert_to_kwargs(args)

    if kwargs is None or argspec.args != list(kwargs.keys()):
        raise ValueError('Invalid args for function: ' + dist_func_str)

    return dist_func(**kwargs)


def _convert_to_kwargs(args):
    """
    converts string of key=val, ..., key=val to dictionary
    :param args: to convert
    :return: dictionary of key values
    """
    parts = args.split(',')
    kwargs = {}
    for part in parts:
        keyval = part.split('=')
        if len(keyval) != 2:
            return None
        kwargs[keyval[0].strip()] = float(keyval[1].strip())
    return kwargs
