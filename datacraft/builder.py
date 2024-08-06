"""
Module for parsing and helper functions for specs
"""
import copy
import json
import logging
from typing import Dict, List, TypeVar, Type
from typing import Generator
from dataclasses import dataclass, fields, MISSING, is_dataclass

from . import registries
from .loader import preprocess_spec, field_loader
from .outputs import OutputHandlerInterface
from .supplier import key_suppliers
from .supplier.model import DataSpec, RecordProcessor
from .exceptions import SpecException

_log = logging.getLogger(__name__)

T = TypeVar('T')


def _ensure_dataclass(data_class: Type[T]):
    """
    Ensures that the provided class is a data class.

    Args:
        data_class: The class to check.

    Raises:
        TypeError: If the provided class is not a data class.
    """
    if not is_dataclass(data_class):
        raise TypeError(f"Expected a dataclass type, got {type(data_class).__name__}")


def _from_dict(data_class: Type[T], data: dict) -> T:
    """
    Convert a dictionary to an instance of a given data class.

    Args:
        data_class: The data class to convert to.
        data: The dictionary to convert.

    Returns:
        An instance of the data class populated with the data from the dictionary.
    """
    field_types = {f.name: f.type for f in fields(data_class)}
    kwargs = {}
    for f in fields(data_class):
        if f.name in data:
            value = data[f.name]
            if isinstance(value, dict) and not isinstance(field_types[f.name], type):
                value = _from_dict(field_types[f.name], value)
            kwargs[f.name] = value
        elif f.default is not MISSING:
            kwargs[f.name] = f.default
        elif f.default_factory is not MISSING:  # For fields with default_factory
            kwargs[f.name] = f.default_factory()
        else:
            raise KeyError(f"Missing required field: {f.name} for {data_class.__name__}")
    return data_class(**kwargs)


def parse_spec(raw_spec: dict) -> DataSpec:
    """
    Parses the raw spec into a DataSpec object. Takes in specs that may contain shorthand specifications. This is
    helpful if the spec is going to be reused in different scenarios.  Otherwise, prefer the generator or entries
    functions.

    Args:
        raw_spec: raw dictionary that conforms to JSON spec format

    Returns:
        the fully parsed and loaded spec

    Examples:
        >>> import datacraft
        >>> raw_spec = { "field": {"type": "values", "data": [10, 100, 1000]}}
        >>> spec = datacraft.parse_spec(raw_spec)
        >>> record = list(spec.generator(1))
    """
    specs = preprocess_spec(raw_spec)
    return _DataSpecImpl(specs)


def entries(raw_spec: Dict[str, Dict], iterations: int, **kwargs) -> List[dict]:
    """
    Creates n entries/records from the provided spec

    Args:
        raw_spec: to create entries for
        iterations: number of iterations before max

    Keyword Args:
        processor: (RecordProcessor): For any Record Level transformations such templating or formatters
        output: (OutputHandlerInterface): For any field or record level output
        data_dir (str): path the data directory with csv files and such
        enforce_schema (bool): If schema validation should be applied where possible

    Returns:
        the list of N entries/records

    Examples:
        >>> import datacraft
        >>> field_spec = {
        ...     "id": {"type": "uuid"},
        ...     "timestamp": {"type": "date.iso.millis"},
        ...     "handle": {"type": "cc-word", "config": { "min": 4, "max": 8, "prefix": "@" } }
        ... }
        >>> print(*datacraft.entries(spec, 3), sep='\\n')
        {'id': '40bf8be1-23d2-4e93-9b8b-b37103c4b18c', 'timestamp': '2050-12-03T20:40:03.709', 'handle': '@WPNn'}
        {'id': '3bb5789e-10d1-4ae3-ae61-e0682dad8ecf', 'timestamp': '2050-11-20T02:57:48.131', 'handle': '@kl1KUdtT'}
        {'id': '474a439a-8582-46a2-84d6-58bfbfa10bca', 'timestamp': '2050-11-29T18:08:44.971', 'handle': '@XDvquPI'}
    """
    return list(generator(raw_spec, iterations, **kwargs))


def record_entries(data_class: Type[T], raw_spec: Dict[str, Dict], iterations: int, **kwargs) -> List[T]:
    """
    Creates a list of instances of a given data class from the provided spec.

    Args:
        data_class: The data class to create instances of.
        raw_spec: Specification to create entries for.
        iterations: Number of iterations before max.

    Keyword Args:
        processor: (RecordProcessor): For any Record Level transformations such templating or formatters.
        output: (OutputHandlerInterface): For any field or record level output.
        data_dir (str): Path to the data directory with CSV files and such.
        enforce_schema (bool): If schema validation should be applied where possible.

    Returns:
        List of instances of the data class.

    Examples:
        >>> @dataclass
        >>> class Entry:
        ...     id: str
        ...     timestamp: str
        ...     handle: str
        >>> raw_spec = {
        ...     "id": {"type": "uuid"},
        ...     "timestamp": {"type": "date.iso.millis"},
        ...     "handle": {"type": "cc-word", "config": { "min": 4, "max": 8, "prefix": "@" } }
        ... }
        >>> print(*record_entries(Entry, raw_spec, 3), sep='\\n')
        Entry(id='d5aeb7fa-374c-4228-8645-e8953165f163', timestamp='2024-07-03T04:10:10.016', handle='@DAHQDSsF')
        Entry(id='acde6f46-4692-45a7-8f0c-d0a8736c4386', timestamp='2024-07-06T17:43:36.653', handle='@vBTf71sP')
        Entry(id='4bb5542f-bf7d-4237-a972-257e24a659dd', timestamp='2024-08-01T03:06:49.724', handle='@gzfY_akS')
    """
    _ensure_dataclass(data_class)
    list_of_maps = entries(raw_spec, iterations, **kwargs)
    return [_from_dict(data_class, entry) for entry in list_of_maps]


def generator(raw_spec: Dict[str, Dict], iterations: int, **kwargs) -> Generator:
    """
    Creates a generator for the raw spec for the specified iterations

    Args:
        raw_spec: to create generator for
        iterations: number of iterations before max

    Keyword Args:
        processor: (RecordProcessor): For any Record Level transformations such templating or formatters
        output: (OutputHandlerInterface): For any field or record level output
        data_dir (str): path the data directory with csv files and such
        enforce_schema (bool): If schema validation should be applied where possible

    Yields:
        Records or rendered template strings

    Returns:
        the generator for the provided spec
    """
    return _DataSpecImpl(copy.deepcopy(raw_spec)).generator(iterations, **kwargs)


def record_generator(data_class: Type[T], raw_spec: Dict[str, Dict], iterations: int, **kwargs) -> Generator[
    T, None, None]:
    """
    Creates a generator that yields instances of a given data class from the provided spec.

    Args:
        data_class: The data class to create instances of.
        raw_spec: Specification to create generator for.
        iterations: Number of iterations before max.

    Keyword Args:
        processor: (RecordProcessor): For any Record Level transformations such templating or formatters.
        output: (OutputHandlerInterface): For any field or record level output.
        data_dir (str): Path to the data directory with CSV files and such.
        enforce_schema (bool): If schema validation should be applied where possible.

    Yields:
        Instances of the data class.

    Returns:
        The generator for the provided spec.
    """
    _ensure_dataclass(data_class)

    data_spec_impl = _DataSpecImpl(copy.deepcopy(raw_spec))
    for entry in data_spec_impl.generator(iterations, **kwargs):
        yield _from_dict(data_class, entry)


def values_for(field_spec: Dict[str, Dict], iterations: int, **kwargs) -> List[dict]:
    """
    Creates n entries/records from the provided spec

    Args:
        field_spec: to create values from
        iterations: number of iterations before max

    Keyword Args:
        enforce_schema (bool): If schema validation should be applied where possible

    Returns:
        the list of N values

    Raises:
        SpecException if field_spec is not valid

    Examples:
        >>> import datacraft
        >>> datacraft.values_for({"type": "uuid"}, 3)
        ['3ab92d2f-58d5-4328-a60e-72ee616199eb', 'cd5d5b64-ff25-4a2f-b69e-5a8c39841fc2', '2326f5c4-1b47-4913-8575-a71950f0fcce']
        >>> datacraft.values_for({"type": "ip", "config": {"prefix": "address:"}}, 3)
        ['address:243.228.123.130', 'address:4.22.163.89', 'address:175.230.40.87']
        >>> datacraft.values_for({"type": "values", "data": ["cat", "dog", "dragon"]}, 3)
        ['cat', 'dog', 'dragon']
    """
    if field_spec is None or not isinstance(field_spec, dict):
        raise SpecException('Field spec must be a dictionary')
    if 'type' not in field_spec:
        raise SpecException(f'Invalid field spec, no type included: {json.dumps(field_spec)}')
    raw_spec = {"temp": field_spec}
    records = list(generator(raw_spec, iterations, **kwargs))
    return [r['temp'] for r in records]


class _DataSpecImpl(DataSpec):
    """ Implementation for DataSpec """

    def generator(self, iterations: int, **kwargs):
        processor: RecordProcessor = kwargs.get('processor', None)
        data_dir = kwargs.get('data_dir', registries.get_default('data_dir'))
        enforce_schema = kwargs.get('enforce_schema', False)
        exclude_internal = kwargs.get('exclude_internal', False)
        output: OutputHandlerInterface = kwargs.get('output', None)
        loader = field_loader(self.raw_spec, data_dir=data_dir, enforce_schema=enforce_schema)

        key_provider = key_suppliers.from_spec(loader.spec)

        for i in range(0, iterations):
            group, keys = key_provider.get()
            record = {}
            for key in keys:
                value = loader.get(key).next(i)
                if output:
                    output.handle(key, value)
                record[key] = value
            if output:
                output.finished_record(i, group, exclude_internal)
                if i == iterations - 1:
                    output.finished_iterations()
            if processor is not None:
                yield processor.process(record)
            else:
                yield record

    def to_pandas(self, iterations):
        try:
            import pandas  # type: ignore
        except ModuleNotFoundError:
            _log.error('pandas not installed, please pip/conda install pandas to allow conversion')
            return None
        records = list(self.generator(iterations))
        return pandas.json_normalize(records)
