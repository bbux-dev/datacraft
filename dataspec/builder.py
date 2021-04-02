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
        self.field_groups = []
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

    def add_field_group(self, field_group: Union[List[str], Dict[str, Dict]]):
        """
        Add a single field group
        :param field_group: to add
        :return: self for chaining invocations
        """
        self.field_groups.append(field_group)
        return self

    def add_field_groups(self, field_groups: Union[List[List[str]], List[Dict[str, Dict]]]):
        """ Add all field groups to list of field groups """
        for entry in field_groups:
            self.add_field_group(entry)
        return self

    def to_spec(self):
        """
        Generates the spec from the provided fields, refs, and field_groups
        :return:
        """
        spec = {}
        spec.update(self.fields)
        if len(self.refs) > 0:
            spec['refs'] = self.refs
        if len(self.field_groups) > 0:
            self._configure_field_groups(spec)

        return spec

    def _configure_field_groups(self, spec):
        """
        Adds the field_groups element to the spec if needed and defined
        """
        all_dict = all(isinstance(entry, dict) for entry in self.field_groups)
        if all_dict:
            flattened = {}
            for entry in self.field_groups:
                flattened.update(entry)
            spec['field_groups'] = flattened
        all_list = all(isinstance(entry, list) for entry in self.field_groups)
        if all_list:
            spec['field_groups'] = self.field_groups


def single_field(name: str, spec):
    """ Creates Builder for single field and spec """
    return Builder().add_field(name, spec)


def weighted_field_group(key: str, fields: List[str], weight: float):
    return {
        key: {
            "weight": weight,
            "fields": fields
        }
    }


def named_field_group(key: str, fields: List[str]):
    return {
        key: fields
    }


def values(data: Union[int, float, str, bool, List, Dict[str, float]], **config):
    """
    Constructs a values spec for the data
    :param data: to use to supply values
    :param config: in **kwargs format
    :return: the values spec
    """
    spec = {
        "type": "values",
        "data": data
    }
    if len(config) > 0:
        spec['config'] = config
    return spec


def combine(refs: List[str] = None, fields: List[str] = None, **config):
    spec = {
        "type": "combine",
    }
    if len(config) > 0:
        spec['config'] = config
    if refs is not None:
        spec['refs'] = refs
    if fields is not None:
        spec['fields'] = fields
    return spec


def combine_list(refs: List[List[str]] = None, **config):
    spec = {
        "type": "combine-list",
        "refs": refs
    }
    if len(config) > 0:
        spec['config'] = config
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
        "data": [start, end, step]
    }
    if len(config) > 0:
        spec['config'] = config
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
        "data": [start, end]
    }
    if len(config) > 0:
        spec['config'] = config
    return spec


def date(**config):
    """
    Constructs a date spec
    :param config: in **kwargs format
    :return: the date spec
    """
    spec = {
        "type": "date"
    }
    if len(config) > 0:
        spec['config'] = config
    return spec


def date_iso(**config):
    """
    Constructs a date_iso spec
    :param config: in **kwargs format
    :return: the date_iso spec
    """
    spec = {
        "type": "date.iso"
    }
    if len(config) > 0:
        spec['config'] = config
    return spec


def date_iso_us(**config):
    """
    Constructs a date_iso_us spec
    :param config: in **kwargs format
    :return: the date_iso_us spec
    """
    spec = {
        "type": "date.iso.us"
    }
    if len(config) > 0:
        spec['config'] = config
    return spec


def uuid(**config):
    """
    Constructs a uuid spec
    :param config: in **kwargs format
    :return: the uuid spec
    """
    spec = {
        "type": "uuid"
    }
    if len(config) > 0:
        spec['config'] = config
    return spec


def char_class(data, **config):
    """
    Constructs a char_class spec
    :param cc_abbrev: alternative type abbreviation i.e. ascii, cc-ascii, visible, cc-visible
    :param data: either known character class or set of characters to use for sampling from
    :param config: in **kwargs format
    :return: the char_class spec
    """
    spec = {
        "type": "char_class",
        "data": data
    }
    if len(config) > 0:
        spec['config'] = config
    return spec


def char_class_abbrev(cc_abbrev: str, **config):
    """
    Constructs a char_class spec
    :param cc_abbrev: alternative type abbreviation i.e. ascii, cc-ascii, visible, cc-visible
    :param config: in **kwargs format
    :return: the char_class spec
    """
    if cc_abbrev.startswith('cc-'):
        abbrev = cc_abbrev
    else:
        abbrev = 'cc-' + cc_abbrev
    spec = {
        "type": abbrev
    }
    if len(config) > 0:
        spec['config'] = config
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
        "data": data
    }
    if len(config) > 0:
        spec['config'] = config
    return spec


def geo_lat(**config):
    """
    Constructs a geo_lat spec
    :param config: in **kwargs format
    :return: the geo_lat spec
    """
    spec = {
        "type": "geo.lat"
    }
    if len(config) > 0:
        spec['config'] = config
    return spec


def geo_long(**config):
    """
    Constructs a geo_long spec
    :param config: in **kwargs format
    :return: the geo_long spec
    """
    spec = {
        "type": "geo.long"
    }
    if len(config) > 0:
        spec['config'] = config
    return spec


def geo_pair(**config):
    """
    Constructs a geo_pair spec
    :param config: in **kwargs format
    :return: the geo_pair spec
    """
    spec = {
        "type": "geo.pair"
    }
    if len(config) > 0:
        spec['config'] = config
    return spec


def ip(**config):
    """
    Constructs a ip spec
    :param config: in **kwargs format
    :return: the ip spec
    """
    spec = {
        "type": "ip"
    }
    if len(config) > 0:
        spec['config'] = config
    return spec


def ipv4(**config):
    """
    Constructs a ipv4 spec
    :param config: in **kwargs format
    :return: the ipv4 spec
    """
    spec = {
        "type": "ipv4"
    }
    if len(config) > 0:
        spec['config'] = config
    return spec


def ip_precise(**config):
    """
    Constructs a ip_precise spec
    :param config: in **kwargs format
    :return: the ip_precise spec
    """
    spec = {
        "type": "ip.precise"
    }
    if len(config) > 0:
        spec['config'] = config
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
        "data": data
    }
    if len(config) > 0:
        spec['config'] = config
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
        "type": "select_list_subset"
    }
    if len(config) > 0:
        spec['config'] = config
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
        "type": "csv"
    }
    if len(config) > 0:
        spec['config'] = config
    return spec


def csv_select(data: Dict[str, int] = None, **config):
    """
    Constructs a csv_select spec
    :param data: Mapping of field name to one based column number
    :param config: in **kwargs format
    :return: the csv_select spec
    """
    spec = {
        "type": "csv_select"
    }
    if len(config) > 0:
        spec['config'] = config
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
        "fields": fields
    }
    if len(config) > 0:
        spec['config'] = config
    return spec


def configref(**config):
    """
    Constructs a configref spec
    :param config: in **kwargs format
    :return: the configref spec
    """
    spec = {
        "type": "configref"
    }
    if len(config) > 0:
        spec['config'] = config
    return spec
