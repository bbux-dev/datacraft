"""
Module for key providers

A KeyProvider is used to supply the names of fields that should be used in the current record. Some times all the fields
will be used for every iteration.  Other times there will be different fields used in different records. This module
provides classes that provide these fields according to various schemes such as rotating lists or weighted lists.

"""
from typing import List, Tuple, Union, Dict
import json

from .model import DataSpec, KeyProviderInterface, ValueSupplierInterface
from .exceptions import SupplierException
from .common import weighted_values_explicit

_ROOT_KEYS = ['refs', 'field_groups']


def from_spec(specs: Union[dict, DataSpec]) -> KeyProviderInterface:
    """
    creates the appropriate key provider for the fields from the supplied spec

    if no field_groups key found, returns KeyProvider with all the fields provided for every iteration

    if field_groups is specified it can take one of three forms:

    1. List[List[str]] i.e:

    .. code-block:: json

        { "field_groups": [
            ["one", "two"],
            ["one", "two", "three"]
          ]
        }


    2. Dict[str, List[str]] -> With weights as keys and fields specified i.e.

    .. code-block:: json

        {
          "field_groups": {
            "0.7": ["one", "two"]
            "0.3": ["one", "two", "three"]
          }
        }


    3. Dict[str, List[str]] -> With names as keys and fields specified i.e.

    .. code-block:: json

        {
          "field_groups": {
            "missing_three": ["one", "two"]
            "all_there": ["one", "two", "three"]
          }
        }

    Returns:
        Appropriate KeyProvider
    """
    if isinstance(specs, DataSpec):
        raw_spec = specs.raw_spec
    else:
        raw_spec = specs
    if 'field_groups' in raw_spec:
        field_groups = raw_spec['field_groups']
        if isinstance(field_groups, dict):
            try:
                # check if all of the keys are numeric
                [float(key) for key in field_groups.keys()]
                return _create_weighted_key_provider(field_groups)
            except ValueError:
                # must be named variety
                return _create_rotating_lists_key_provider(field_groups)
        if isinstance(field_groups, list):
            return _create_rotating_lists_key_provider(field_groups)
    # default when no field groups specified
    keys = [key for key in raw_spec.keys() if key not in _ROOT_KEYS]
    return _KeyListProvider(keys)


class _KeyListProvider(KeyProviderInterface):
    """ Class the provides static list of keys """

    def __init__(self, keys: List[str]):
        self.keys = keys

    def get(self):
        return 'ALL', self.keys


class _RotatingKeyListProvider(KeyProviderInterface):
    """Class the provides keys from list of various keys in rotating manner """

    def __init__(self, keys: List[Tuple[str, List[str]]]):
        """
        Keys should be list of tuples of form:
         [(name1, [key1, key2, ..., keyN]), (name2, [key1, key2, ...keyN), ...]

        Args:
            keys: to rotate through
        """
        self.keys = keys
        self.cnt = 0

    def get(self):
        idx = self.cnt % len(self.keys)
        self.cnt += 1
        entry = self.keys[idx]
        # entry is tuple so should
        return entry


class _WeightedGroupKeyProvider(KeyProviderInterface):
    """Class that supplies keys according to weighted scheme """

    def __init__(self, field_groups: dict, supplier: ValueSupplierInterface):
        self.field_groups = field_groups
        self.supplier = supplier

    def get(self):
        key = self.supplier.next(0)
        if key not in self.field_groups:
            raise SupplierException(f'Key: {key} not found: {json.dumps(self.field_groups)}')
        return key, self.field_groups[key]


def _create_weighted_key_provider(field_groups: Dict) -> KeyProviderInterface:
    """Creates a weighted field group key provide for the supplied field_groups """
    keys = list(field_groups.keys())
    weights = [float(key) for key in keys]
    supplier = weighted_values_explicit(keys, weights)
    return _WeightedGroupKeyProvider(field_groups, supplier)


def _create_rotating_lists_key_provider(field_groups: Union[List, Dict]) -> KeyProviderInterface:
    """Creates a rotating key list provider for the field_groups """
    if isinstance(field_groups, list):
        keys = [('_'.join(keys_list), keys_list) for keys_list in field_groups]
    elif isinstance(field_groups, dict):
        keys = list(field_groups.items())
    else:
        raise ValueError('Invalid type for field_groups only one of list or dict allowed')
    return _RotatingKeyListProvider(keys)
