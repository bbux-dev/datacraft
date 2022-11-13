"""module for refs type datacraft registry functions"""
import re
import json
import logging
from typing import Dict

import datacraft
from datacraft import ValueSupplierInterface
from . import common
from . import schemas

_log = logging.getLogger(__name__)
_REPLACE_KEY = 'replace'
_REGEX_REPLACE_KEY = 'regex_replace'


@datacraft.registry.schemas(_REPLACE_KEY)
def _get_replace_schema():
    """ schema for ref type """
    return schemas.load(_REPLACE_KEY)


@datacraft.registry.schemas(_REGEX_REPLACE_KEY)
def _get_regex_replace_schema():
    """ schema for ref type """
    # same schema for both
    return schemas.load(_REPLACE_KEY)


@datacraft.registry.types(_REPLACE_KEY)
def _configure_replace_supplier(field_spec: dict, loader: datacraft.Loader):
    """ configures supplier for replace type """
    mappings, wrapped = _validate_and_load(field_spec, loader)
    return _ReplaceSupplier(wrapped=wrapped, replacements=mappings)


@datacraft.registry.types(_REGEX_REPLACE_KEY)
def _configure_regex_replace_supplier(field_spec: dict, loader: datacraft.Loader):
    """ configures supplier for regex_replace type """
    mappings, wrapped = _validate_and_load(field_spec, loader)
    return _RegexReplaceSupplier(wrapped=wrapped, replacements=mappings)


def _validate_and_load(field_spec, loader):
    if any(key not in field_spec for key in ["ref", "data"]):
        raise datacraft.SpecException('ref and data fields required for replace spec: ' + json.dumps(field_spec))
    mappings = field_spec.get('data')
    if not isinstance(mappings, dict):
        raise datacraft.SpecException('data element must be dictionary for replace spec: ' + str(field_spec))
    wrapped = loader.get(field_spec.get('ref'))
    return mappings, wrapped


@datacraft.registry.usage(_REPLACE_KEY)
def _example_replace_usage():
    example = {
        "field": ["foo", "bar", "baz"],
        "replacement": {
            "type": "replace",
            "ref": "field",
            "data": {
                "ba": "fi"
            }
        }
    }
    return common.standard_example_usage(example, 3)


@datacraft.registry.usage(_REGEX_REPLACE_KEY)
def _example_regex_replace_usage():
    example = {
        "field": ["val 1", "val 2", "val 3 1", "val 3 2"],
        "replacement": {
            "type": "regex_replace",
            "ref": "field",
            "data": {
                "\\s": "_"
            }
        }
    }
    return common.standard_example_usage(example, 4, pretty=True)


class _ReplaceSupplier(ValueSupplierInterface):
    """
    Value supplier that replaces one or more values in the output of another supplier
    """

    def __init__(self,
                 wrapped: ValueSupplierInterface,
                 replacements: Dict[str, str]):
        """
        Args:
            wrapped: supplier to replace values from
            replacements: mapping of value string to replacement value string
        """
        self.wrapped = wrapped
        self.replacements = replacements

    def next(self, iteration):
        modified = str(self.wrapped.next(iteration))
        for value, replacement in self.replacements.items():
            modified = modified.replace(value, str(replacement))
        return modified


class _RegexReplaceSupplier(ValueSupplierInterface):
    """
    Value supplier that replaces one or more values in the output of another supplier using regular expression
    substitution
    """

    def __init__(self,
                 wrapped: ValueSupplierInterface,
                 replacements: Dict[str, str]):
        """
        Args:
            wrapped: supplier to replace values from
            replacements: mapping of value string to replacement value string
        """
        self.wrapped = wrapped
        self.replacements = replacements

    def next(self, iteration):
        modified = str(self.wrapped.next(iteration))
        for pattern, replacement in self.replacements.items():
            regex = re.compile(pattern)
            modified = re.sub(regex, str(replacement), modified)
        return modified
