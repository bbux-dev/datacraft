"""
Loader module is the interface into the datacraft data generation utility.  This class handles loading, parsing and
delegating the handling of various data types.
"""

import json
import logging
from typing import Any, Dict, Union
from abc import ABC, abstractmethod

from . import utils, suppliers, preprocessor, spec_formatters
from .exceptions import SpecException
from .supplier.model import DataSpec, ValueSupplierInterface
from .schemas import validate_schema_for_spec
from .registries import lookup_type, lookup_schema, Registry

_log = logging.getLogger(__name__)


class Refs:
    """Holder object for references """

    def __init__(self, refspec):
        if refspec:
            self.refspec = refspec
        else:
            self.refspec = {}

    def get(self, key):
        """
        get the ref for the key

        Args:
            key: to use for lookup

        Returns:
            The ref
        """
        return self.refspec.get(key)


class Loader(ABC):
    """Parent object for loading value suppliers from specs """

    @property
    @abstractmethod
    def spec(self):
        """get the preprocessed field specs for this loader"""

    @abstractmethod
    def get(self, key: str) -> ValueSupplierInterface:
        """
        Retrieve the value supplier for the given field or ref key

        Args:
            key: key to for field or ref name

        Returns:
            the Value Supplier for the given key

        Raises:
            SpecException if key not found
        """

    @abstractmethod
    def get_from_spec(self, field_spec: Any) -> ValueSupplierInterface:
        """
        Retrieve the value supplier for the given field spec

        Args:
            field_spec: dictionary spec or literal values

        Returns:
            the Value Supplier for the given spec

        Raises:
            SpecException if unable to resolve the spec with appropriate handler for the type
        """

    @abstractmethod
    def get_ref(self, key: str) -> dict:
        """
        returns the spec for the ref with the provided key

        Args:
             key: key to lookup ref by

        Returns:
            Ref for key
        """


def field_loader(data_spec, data_dir='./data', enforce_schema=False) -> Loader:
    """Loader for loading fields suppliers from data spec

    Args:
        data_spec: to use for loading
        data_dir: where to look for external data files
        enforce_schema: if schemas should be enforced

    Returns:
        Loader for this spec
    """
    return _LoaderImpl(data_spec, data_dir, enforce_schema)


class _LoaderImpl(Loader):
    """Field loader implementation """

    def __init__(self, data_spec, data_dir='./data', enforce_schema=False):
        raw_spec = utils.get_raw_spec(data_spec)
        self.specs = preprocess_spec(raw_spec)
        self.datadir = data_dir
        self.enforce_schema = enforce_schema
        self.cache = {}
        self.refs = Refs(self.specs.get('refs'))

    @property
    def spec(self):
        return self.specs

    def get(self, key: str) -> ValueSupplierInterface:
        """
        Retrieve the value supplier for the given field or ref key

        Args:
            key: key to for field or ref name

        Returns:
            the Value Supplier for the given key

        Raises:
            SpecException if key not found
        """
        if key in self.cache:
            return self.cache[key]

        data_spec = self.specs.get(key)
        if data_spec is None:
            data_spec = self.refs.get(key)
        if data_spec is None:
            raise SpecException("No key " + key + " found in specs")
        supplier = self.get_from_spec(data_spec)
        self.cache[key] = supplier
        return supplier

    def get_from_spec(self, field_spec: Any) -> ValueSupplierInterface:
        """
        Retrieve the value supplier for the given field spec

        Args:
            field_spec: dictionary spec or literal values

        Returns:
            the Value Supplier for the given spec

        Raises:
            SpecException if unable to resolve the spec with appropriate handler for the type
        """
        if isinstance(field_spec, list):
            spec_type = None
        elif isinstance(field_spec, dict):
            spec_type = field_spec.get('type')
        else:
            # assume it is data, so values?
            spec_type = 'values'

        if spec_type == 'config_ref':
            raise SpecException(f'Cannot use config_ref as source of data: {json.dumps(field_spec)}')
        if spec_type is None:
            if self.enforce_schema:
                _validate_schema_for_spec('values', field_spec)
            supplier = suppliers.values(field_spec)
        else:
            handler = lookup_type(spec_type)
            if handler is None:
                raise SpecException('Unable to load handler for: ' + json.dumps(field_spec))
            if self.enforce_schema:
                _validate_schema_for_spec(spec_type, field_spec)
            supplier = handler(field_spec, self)
        config = field_spec.get('config', {})
        # special case
        if spec_type == 'nested':
            return supplier
        return suppliers.alter(supplier, **config)

    def get_ref(self, key: str) -> dict:
        """
        returns the spec for the ref with the provided key

        Args:
             key: key to lookup ref by

        Returns:
            Ref for key
        """
        return self.refs.get(key)


def _validate_schema_for_spec(spec_type: str, field_spec: dict):
    """ validates the schema for the given spec type and field spec """
    type_schema = lookup_schema(spec_type)
    if type_schema is None:
        return
    validate_schema_for_spec(spec_type, field_spec, type_schema)


def preprocess_and_format(raw_spec: dict) -> str:
    """Runs all preprocessors and formats spec as string

    Args:
        raw_spec: to process

    Returns:
        formatted spec as a string

    Examples:
        >>> import datacraft
        >>> @datacraft.registry.usage('custom')
        ... def _custom_type_usage():
        ...     spec = datacraft.preprocess_and_format(_EXAMPLE)
        ...     return f'Example Spec:\\n{spec}'
    """
    preprocessed = preprocess_spec(raw_spec)
    return spec_formatters.format_json(preprocessed)


def preprocess_spec(data_spec: Union[Dict[str, Dict], DataSpec]):
    """
    Uses the registered preprocessors to cumulatively update the spec

    Args:
        data_spec: to preprocess

    Returns:
        updated version of the spec after all preprocessors have run on it
    """
    raw_spec = utils.get_raw_spec(data_spec)
    updated = dict(raw_spec)
    preprocessors = Registry.preprocessors.get_all()
    for name in preprocessors:
        preprocessor_func = Registry.preprocessors.get(name)
        _log.debug('Running Preprocessor: %s', name)
        processed = preprocessor_func(updated)
        if processed is None:
            _log.error('Invalid preprocessor %s, returned None instead of updated spec, skipping', name)
            continue
        updated = processed
    return updated
