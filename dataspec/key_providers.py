""" Module for key providers """
from typing import List
import json
from dataspec import suppliers, ValueSupplierInterface
from .exceptions import SpecException

ROOT_KEYS = ['refs', 'field_groups']


class KeyProviderInterface:
    """ Interface for KeyProviders """

    def get(self) -> List[str]:
        """ get the next set of field names to process """


def from_spec(specs: dict) -> KeyProviderInterface:
    """ creates the appropriate key provider for the fields from the supplied spec """
    if 'field_groups' in specs:
        field_groups = specs['field_groups']
        if isinstance(field_groups, dict):
            return _create_weighted_field_group_key_provider(field_groups)
        if isinstance(field_groups, list):
            return _create_rotating_lists_field_group_key_provider(field_groups)
    keys = [key for key in specs.keys() if key not in ROOT_KEYS]
    return KeyListProvider(keys)


class KeyListProvider(KeyProviderInterface):
    """ Class the provides static list of keys """

    def __init__(self, keys: List[str]):
        self.keys = keys

    def get(self):
        return self.keys


class RotatingKeyListProvider(KeyProviderInterface):
    """ Class the provides keys from list of various keys in rotating manner """

    def __init__(self, keys_lists: List[List[str]]) -> KeyProviderInterface:
        self.keys_lists = keys_lists
        self.cnt = 0

    def get(self):
        idx = self.cnt % len(self.keys_lists)
        self.cnt += 1
        return self.keys_lists[idx]


class WeightedGroupKeyProvider(KeyProviderInterface):
    """ Class that supplies key """

    def __init__(self, field_groups: dict, supplier: ValueSupplierInterface, fields_key: str = 'fields'):
        self.field_groups = field_groups
        self.supplier = supplier
        self.fields_key = fields_key

    def get(self):
        key = self.supplier.next(0)
        if key not in self.field_groups or self.fields_key not in self.field_groups[key]:
            raise SpecException(
                f'Key: {key}, or fields key {self.fields_key} not found: {json.dumps(self.field_groups)}')
        return self.field_groups[key]['fields']


def _create_weighted_field_group_key_provider(field_groups: dict) -> KeyProviderInterface:
    weights = {key: value['weight'] for key, value in field_groups.items()}
    supplier = suppliers.weighted_values(weights)
    return WeightedGroupKeyProvider(field_groups, supplier)


def _create_rotating_lists_field_group_key_provider(field_groups: List[List[str]]) -> KeyProviderInterface:
    """ Creates a rotating key list provider for the groups of fields """
    return RotatingKeyListProvider(field_groups)
