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
_MASKED_KEY = 'masked'


@datacraft.registry.schemas(_REPLACE_KEY)
@datacraft.registry.schemas(_MASKED_KEY)
@datacraft.registry.schemas(_REGEX_REPLACE_KEY)
def _get_regex_replace_schema():
    """ schema for ref type """
    # same schema for both
    return schemas.load(_REPLACE_KEY)


@datacraft.registry.types(_REPLACE_KEY)
def _configure_replace_supplier(field_spec: dict, loader: datacraft.Loader):
    """ configures supplier for replace type """
    mappings, wrapped = _validate_and_load_replace(field_spec, loader)
    return _ReplaceSupplier(wrapped=wrapped, replacements=mappings)

def _validate_and_load_replace(field_spec, loader):
    if any(key not in field_spec for key in ["ref", "data"]):
        raise datacraft.SpecException('ref and data fields required for replace spec: ' + json.dumps(field_spec))
    wrapped = loader.get(field_spec.get('ref'))
    mappings = field_spec.get('data')

    if not isinstance(mappings, dict):
        raise datacraft.SpecException('data element must be dictionary for replace spec: ' + str(field_spec))
    # turn values into value suppliers
    mappings = {k: datacraft.suppliers.values(v) for k, v in mappings.items()}
    return mappings, wrapped

@datacraft.registry.types(_MASKED_KEY)
@datacraft.registry.types(_REGEX_REPLACE_KEY)
def _configure_regex_replace_supplier(field_spec: dict, loader: datacraft.Loader):
    """ configures supplier for regex_replace type """
    mappings, wrapped = _validate_and_load_regex_replace(field_spec, loader)
    return _RegexReplaceSupplier(wrapped=wrapped, replacements=mappings)





def _validate_and_load_regex_replace(field_spec, loader):
    if any(key not in field_spec for key in ["ref", "data"]):
        raise datacraft.SpecException('ref and data fields required for replace spec: ' + json.dumps(field_spec))
    wrapped = loader.get(field_spec.get('ref'))
    mappings = field_spec.get('data')
    # special case where data is just a string that should replace all values
    if isinstance(mappings, str):
        mappings = {'^.*': datacraft.suppliers.values(mappings)}
        return mappings, wrapped

    if not isinstance(mappings, dict):
        raise datacraft.SpecException('data element must be dictionary for replace spec: ' + str(field_spec))
    # turn values into value suppliers
    mappings = {k: datacraft.suppliers.values(v) for k, v in mappings.items()}
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


@datacraft.registry.usage(_MASKED_KEY)
def _example_masked_usage():
    example = {
        "masked_ssn": {
            "type": _MASKED_KEY,
            "ref": "ssn",
            "data": {
                "^.*": "NNN-NN-NNNN"
            }
        },
        "refs": {
            "ssn": ["123-45-6789", "111-22-3333", "555-55-5555"]
        }
    }
    return common.standard_example_usage(example, 3, pretty=True)


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
            replacements: mapping of value string to replacement value supplier
        """
        self.wrapped = wrapped
        self.replacements = replacements

    def next(self, iteration):
        modified = str(self.wrapped.next(iteration))
        for value, supplier in self.replacements.items():
            replacement = supplier.next(iteration)
            modified = modified.replace(value, str(replacement))
        return modified


class _RegexReplaceSupplier(ValueSupplierInterface):
    """
    Value supplier that replaces one or more values in the output of another supplier using regular expression
    substitution
    """

    def __init__(self,
                 wrapped: ValueSupplierInterface,
                 replacements: Dict[str, ValueSupplierInterface]):
        """
        Args:
            wrapped: supplier to replace values from
            replacements: mapping of value string to replacement value supplier
        """
        self.wrapped = wrapped
        self.replacements = replacements

    def next(self, iteration):
        modified = str(self.wrapped.next(iteration))
        for pattern, supplier in self.replacements.items():
            regex = re.compile(pattern)
            replacement = supplier.next(iteration)
            modified = re.sub(regex, str(replacement), modified)
        return modified
