"""
Module for parsing and helper functions for specs
"""
import copy
import logging
from typing import Dict, List
from typing import Generator

from . import registries
from .loader import preprocess_spec, field_loader
from .outputs import OutputHandlerInterface
from .supplier import key_suppliers
from .supplier.model import DataSpec, RecordProcessor

_log = logging.getLogger(__name__)


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
        >>> spec = {
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
