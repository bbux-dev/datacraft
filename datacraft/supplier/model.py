"""
Module to hold models for core data structures and classes
"""
from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import Union, Tuple, List, Any, Generator, Dict


class DataSpec(dict):
    """
    Class representing a DataSpec object
    """
    def __init__(self, raw_spec: dict):
        super().__init__()
        self.raw_spec = raw_spec

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

    def __len__(self):
        return len(self.raw_spec)

    def get(self, *args, **kwargs):
        return self.raw_spec.get(*args, **kwargs)

    def items(self):
        return self.raw_spec.items()

    def keys(self):
        return self.raw_spec.keys()

    def values(self):
        return self.raw_spec.values()

    def pop(self, k, d=None):
        return self.raw_spec.pop(k, d)

    @abstractmethod
    def generator(self, iterations: int, **kwargs) -> Generator:
        """
        Creates a generator that will produce records or render the template for each record

        Args:
            iterations: number of iterations to execute
            **kwargs:

        Keyword Args:
            processor: (RecordProcessor): For any Record Level transformations such templating or formatters
            output: (OutputHandlerInterface): For any field or record level output
            data_dir (str): path the data directory with csv files and such
            enforce_schema (bool): If schema validation should be applied where possible

        Yields:
            Records or rendered template strings

        Examples:
            >>> import datacraft
            >>> raw_spec {'name': ['bob', 'bobby', 'robert', 'bobo']}
            >>> spec = datacraft.parse_spec(raw_spec)
            >>> template = 'Name: {{ name }}'
            >>> processor = datacraft.outputs.processor(template=template)
            >>> generator = spec.generator(
            ...     iterations=4,
            ...     processor=processor)
            >>> record = next(generator)
            >>> print(record)
            Name: bob
        """

    @abstractmethod
    def to_pandas(self, iterations: int):
        """
        Converts iterations number of records into a pandas DataFrame

        Args:
            iterations: number of iterations to run / records to generate

        Returns:
            DataFrame with records as rows
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


class RecordProcessor(ABC):
    """A Class that takes in a generated record and returns it formatted as a string for output"""

    @abstractmethod
    def process(self, record: Union[list, dict]) -> str:
        """
        Processes the given record into the appropriate output string

        Args:
            record: generated record for current iteration

        Returns:
            The formatted record
        """


class OutputHandlerInterface(ABC):
    """Interface four handling generated output values"""

    @abstractmethod
    def handle(self, key: str, value: Any):
        """
        This is called each time a new value is generated for a given field

        Args:
            key: the field name
            value: the new value for the field
        """

    @abstractmethod
    def finished_record(self,
                        iteration: int,
                        group_name: str,
                        exclude_internal: bool = False):
        """
        This is called whenever all of the fields for a record have been generated for one iteration

        Args:
            iteration: iteration we are on
            group_name: group this record is apart of
            exclude_internal: if external fields should be excluded from output record
        """

    @abstractmethod
    def finished_iterations(self):
        """This is called when all iterations have been completed"""


class CasterInterface(ABC):
    """
    Interface for Classes that cast objects to different types
    """

    @abstractmethod
    def cast(self, value: Any) -> Any:
        """
        casts the value according to the specified type

        Args:
            value: to cast

        Returns:
            the cast form of the value

        Raises:
            SpecException when unable to cast value
        """


class ResettableIterator(Iterator, ABC):
    """Iterator class that can be reset to the beginning of the iteration """
    @abstractmethod
    def reset(self):
        """
        This will reset the iterator to the initial state for another full round of iteration
        """
