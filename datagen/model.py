"""
Module to hold models for core data structures and classes
"""
from abc import ABC, abstractmethod
from typing import Tuple, List


class DataSpec(dict):
    """
    Class representing a DataSpec object
    """

    def __delitem__(self, key):
        return self.raw_spec.__delitem__(key)

    def __setitem__(self, key, value):
        return self.raw_spec.__setitem__(key, value)

    def __getitem__(self, key):
        return self.raw_spec.__getitem__(key)

    def __contains__(self, key):
        return self.raw_spec.__contains__(key)

    def __repr__(self):
        return str(self.raw_spec)

    def __str__(self):
        return str(self.raw_spec)

    def pop(self, key):
        return self.raw_spec.pop(key)

    def __init__(self, raw_spec):
        self.raw_spec = raw_spec

    def generator(self, iterations: int, **kwargs):
        """
        Creates a generator that will produce records or render the template for each record

        Args:
            iterations: number of iterations to execute
            **kwargs:

        Keyword Args:
            template (Union[str, Path]): inline string template or path to template on disk
            data_dir (str): path the data directory with csv files and such
            enforce_schema (bool): If schema validation should be applied where possible

        Yields:
            Records or rendered template strings

        Examples:

            >>> import datagen
            >>> builder = datagen.spec_builder()
            >>> builder.values(['bob', 'bobby', 'robert', 'bobo']))
            >>> spec = builder.build()
            >>> template = 'Name: {{ name }}'
            >>> generator = spec.generator(
            ...     iterations=4,
            ...     template=template)
            >>> record = next(generator)
            >>> print(record)
            Name: bob
        """


class Distribution(ABC):
    """
    Interface Class for a numeric distribution such as a Uniform or Gaussian distribution
    """

    @abstractmethod
    def next_value(self) -> float:
        """ get the next value for this distribution """


class ValueSupplierInterface(ABC):
    """
    Interface for Classes that supply values
    """

    @abstractmethod
    def next(self, iteration):
        """
        Produces the next value for the given iteration

        Args:
            iteration: current iteration

        Returns:
            the next value
        """


class KeyProviderInterface(ABC):
    """ Interface for KeyProviders """

    @abstractmethod
    def get(self) -> Tuple[str, List[str]]:
        """get the next set of field names to process

        Returns:
            key_group_name, key_list_for_group_name
        """