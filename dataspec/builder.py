"""
Module for building Data Specs programmatically
"""
from typing import Any, Union, Dict, List
import json
import logging

log = logging.getLogger(__name__)


class Builder:
    """
    Container class for constructing the Data Spec by adding fields, refs, and field_groups

    Basic Usage:

    builder = dataspec.builder.Builder()
    builder.add_fields(
        FIELDNAME1=builder.some_spec(with_args),
        FIELDNAME2=builder.another_spec(with_args)
    )
    builder.add_refs(
        REFNAME1=builder.some_spec(with_args),
        REFNAME2=builder.another_spec(with_args)
    )
    spec = builder.to_spec()
    """

    def __init__(self):
        self.refs = {}
        self.fields = {}
        self.keys = set()

    def add_fields(self, **kwargs):
        """
        Add all fields to the spec. kwargs format should be:

        builder = dataspec.builder.Builder()
        builder.add_fields(
            FIELDNAME1=builder.some_spec(with_args),
            FIELDNAME2=builder.another_spec(with_args)
        )

        :param kwargs: where key is field name and value is a generated spec
        :return: self for chaining invocations
        """
        for key, spec in kwargs.items():
            self.add_field(key, spec)
        return self

    def add_field(self, key: str, spec: dict):
        """
        Add single field to the spec.

        builder = dataspec.builder.Builder()
        builder.add_field("field1", builder.some_spec(with_args)) \
               .add_field("field2", builder.another_spec(with_args))

        :param key: field name
        :param spec: the generate spec for this field
        :return: self for chaining invocations
        """
        if key in self.keys:
            log.warning('%s key already defined, overwriting with %s',
                        key, json.dumps(spec))
        self.keys.add(key)
        self.fields[key] = spec
        return self

    def add_refs(self, **kwargs):
        """
        Add all refs to the spec. kwargs format should be:

        builder = dataspec.builder.Builder()
        builder.add_refs(
            REFNAME1=builder.some_spec(with_args),
            REFNAME2=builder.another_spec(with_args)
        )

        :param kwargs: where key is ref name and value is a generated spec
        :return: self for chaining invocations
        """
        for key, spec in kwargs.items():
            self.add_ref(key, spec)
        return self

    def add_ref(self, key: str, spec: dict):
        """
        Add single ref to the spec.

        builder = dataspec.builder.Builder()
        builder.add_ref("ref1", builder.some_spec(with_args)) \
               .add_ref("ref2", builder.another_spec(with_args))

        :param key: ref name
        :param spec: the generate spec for this ref
        :return: self for chaining invocations
        """
        if key in self.keys:
            log.warning('%s key already defined, overwriting with %s',
                        key, json.dumps(spec))
        self.keys.add(key)
        self.refs[key] = spec
        return self

    def to_spec(self):
        """
        Generates the spec from the provided fields, refs, and field_groups
        :return:
        """
        spec = {}
        spec.update(self.fields)
        spec['refs'] = self.refs
        return spec


def values(data: Union[int, float, str, bool, List, Dict[str, float]], **config):
    """
    Constructs a values spec for the data
    :param data: to use to supply values
    :param config: in **kwargs format
    :return: the values spec
    """
    spec = {
        "type": "values",
        "data": data,
        "config": config
    }
    return spec


def combine(refs: List[str] = None, fields: List[str] = None, **config):
    spec = {
        "type": "combine",
        "config": config
    }
    if refs is not None:
        spec['refs'] = refs
    if fields is not None:
        spec['fields'] = fields
    return spec


def combine_list(refs: List[List[str]] = None, **config):
    spec = {
        "type": "combine-list",
        "config": config,
        "refs": refs
    }
    return spec


def range_spec(start, end, step=1, **config):
    """
    Constructs a range spec
    :param start: start of range inclusive
    :param end: end of range inclusive
    :param step: step for range
    :param config: in **kwargs format
    :return: the range spec
    """
    spec = {
        "type": "range",
        "config": config,
        "data": [start, end, step]
    }
    return spec


def rand_range(start, end, **config):
    """
    Constructs a rand_range spec
    :param start: start of range inclusive
    :param end: end of range inclusive
    :param config: in **kwargs format
    :return: the range spec
    """
    spec = {
        "type": "rand_range",
        "config": config,
        "data": [start, end]
    }
    return spec


def date(**config):
    """
    Constructs a date spec
    :param config: in **kwargs format
    :return: the date spec
    """
    spec = {
        "type": "date",
        "config": config
    }
    return spec


def date_iso(**config):
    """
    Constructs a date_iso spec
    :param config: in **kwargs format
    :return: the date_iso spec
    """
    spec = {
        "type": "date.iso",
        "config": config
    }
    return spec


def date_iso_us(**config):
    """
    Constructs a date_iso_us spec
    :param config: in **kwargs format
    :return: the date_iso_us spec
    """
    spec = {
        "type": "date.iso.us",
        "config": config
    }
    return spec


def uuid(**config):
    """
    Constructs a uuid spec
    :param config: in **kwargs format
    :return: the uuid spec
    """
    spec = {
        "type": "uuid",
        "config": config
    }
    return spec


def char_class(data=None, cc_abbrev=None, **config):
    """
    Constructs a char_class spec
    :param cc_abbrev: alternative type abbreviation i.e. ascii, cc-ascii, visible, cc-visible
    :param data: either known character class or set of characters to use for sampling from
    :param config: in **kwargs format
    :return: the char_class spec
    """
    if data is not None:
        spec = {
            "type": "char_class",
            "config": config,
            "data": data
        }
    if cc_abbrev is not None:
        if not cc_abbrev.startswith('cc-'):
            abbrev = f'cc-{cc_abbrev}'
        else:
            abbrev = cc_abbrev
        spec = {
            "type": abbrev,
            "config": config
        }
    return spec


def unicode_range(data: Union[List[str], List[List[str]]], **config):
    """
    Constructs a unicode_range spec
    :param data: hex start and end unicode ranges or lists of these
    :param config: in **kwargs format
    :return: the unicode_range spec
    """
    spec = {
        "type": "unicode_range",
        "config": config,
        "data": data
    }
    return spec


def geo_lat(**config):
    """
    Constructs a geo_lat spec
    :param config: in **kwargs format
    :return: the geo_lat spec
    """
    spec = {
        "type": "geo_lat",
        "config": config
    }
    return spec


def geo_long(**config):
    """
    Constructs a geo_long spec
    :param config: in **kwargs format
    :return: the geo_long spec
    """
    spec = {
        "type": "geo_long",
        "config": config
    }
    return spec


def geo_pair(**config):
    """
    Constructs a geo_pair spec
    :param config: in **kwargs format
    :return: the geo_pair spec
    """
    spec = {
        "type": "geo_pair",
        "config": config
    }
    return spec


def ip(**config):
    """
    Constructs a ip spec
    :param config: in **kwargs format
    :return: the ip spec
    """
    spec = {
        "type": "ip",
        "config": config
    }
    return spec


def ipv4(**config):
    """
    Constructs a ipv4 spec
    :param config: in **kwargs format
    :return: the ipv4 spec
    """
    spec = {
        "type": "ipv4",
        "config": config
    }
    return spec


def ip_precise(**config):
    """
    Constructs a ip_precise spec
    :param config: in **kwargs format
    :return: the ip_precise spec
    """
    spec = {
        "type": "ip.precise",
        "config": config
    }
    return spec


def weightedref(data: Dict[str, float], **config):
    """
    Constructs a weightedref spec
    :param data: Mapping of ref name to weight
    :param config: in **kwargs format
    :return: the weightedref spec
    """
    spec = {
        "type": "weightedref",
        "config": config,
        "data": data
    }
    return spec


def select_list_subset(data: List[Any] = None, ref: str = None, **config):
    """
    Constructs a select_list_subset spec
    :param data: to select from
    :param ref: that contains data to select from
    :param config: in **kwargs format
    :return: the select_list_subset spec
    """
    spec = {
        "type": "select_list_subset",
        "config": config
    }
    if data is not None:
        spec['data'] = data
    if ref is not None:
        spec['ref'] = ref
    return spec


def csv(**config):
    """
    Constructs a csv spec
    :param config: in **kwargs format
    :return: the csv spec
    """
    spec = {
        "type": "csv",
        "config": config
    }
    return spec


def csv_select(data: Dict[str, int] = None, **config):
    """
    Constructs a csv_select spec
    :param data: Mapping of field name to one based column number
    :param config: in **kwargs format
    :return: the csv_select spec
    """
    spec = {
        "type": "csv_select",
        "config": config
    }
    if data is not None:
        spec['data'] = data
    return spec


def nested(fields: Dict[str, Dict], **config):
    """
    Constructs a nested spec
    :param fields: sub field specifications
    :param config: in **kwargs format
    :return: the nested spec
    """
    spec = {
        "type": "nested",
        "config": config,
        "fields": fields
    }
    return spec


def configref(**config):
    """
    Constructs a configref spec
    :param config: in **kwargs format
    :return: the configref spec
    """
    spec = {
        "type": "configref",
        "config": config
    }
    return spec
