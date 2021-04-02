"""
Module for building Data Specs programmatically
"""


from typing import Any, Union, Dict, List
import json
import logging

log = logging.getLogger(__name__)


class FieldInfo:
    """
    Class for holding info after adding field or ref to spec. Can be passed to specs that use other specs
    like combine
    """

    def __init__(self, key: str, type_name: str, builder=None):
        self.key = key
        self.type_name = type_name
        self.builder = builder


class Builder:
    """
    Container class for constructing the Data Spec by adding fields, refs, and field_groups

    Basic Usage:

    builder = dataspec.builder.Builder()
    builder.values('names', ['amy', 'bob', 'cat', 'dan', 'earl'])
    builder.range('ages', start=22, end=33)
    spec = builder.build()
    """

    def __init__(self, has_refs=True):
        if has_refs:
            self.refs_builder = Builder(False)
        else:
            self.refs_builder = None
        self.fields = {}
        self.field_groups = []
        self.keys = set()

    def values(self, key: str, data: Union[int, float, str, bool, List, Dict[str, float]], **config):
        """
        creates values Field Spec and adds to Data Spec

        :param key: name of ref/field
        :param data: to use to supply values
        :param config: in **kwargs format
        """
        return self._add_field_spec(key, values(data, **config))

    def combine(self, key: str,
                refs: List[Union[str, FieldInfo]] = None,
                fields: List[Union[str, FieldInfo]] = None,
                **config):
        """
        creates combine Field Spec and adds to Data Spec

        :param key: name of ref/field
        :param refs: refs to combine
        :param fields: fields to combine
        :param config: in **kwargs format
        """
        return self._add_field_spec(key, combine(refs, fields, **config))

    def combine_list(self, key: str, refs: List[List[Union[str, FieldInfo]]] = None, **config):
        """
        creates combine-list Field Spec and adds to Data Spec

        :param key: name of ref/field
        :param refs: lists of lists of refs to combine
        :param config: in **kwargs format
        """
        return self._add_field_spec(key, combine_list(refs, **config))

    def range_spec(self, key: str, start: Union[int, float], end: Union[int, float], step: Union[int, float], **config):
        """
        creates range Field Spec and adds to Data Spec

        :param key: name of ref/field
        :param start: start of range inclusive
        :param end: end of range inclusive
        :param step: step for range
        :param config: in **kwargs format
        """
        return self._add_field_spec(key, range_spec(start, end, step, **config))

    def rand_range(self, key: str, start: Union[int, float], end: Union[int, float], **config):
        """
        creates rand_range Field Spec and adds to Data Spec

        :param key: name of ref/field
        :param start: start of range inclusive
        :param end: end of range inclusive
        :param config: in **kwargs format
        """
        return self._add_field_spec(key, rand_range(start, end, **config))

    def date(self, key: str, **config):
        """
        creates date Field Spec and adds to Data Spec

        :param key: name of ref/field
        :param config: in **kwargs format
        """
        return self._add_field_spec(key, date(**config))

    def date_iso(self, key: str, **config):
        """
        creates date.iso Field Spec and adds to Data Spec

        :param key: name of ref/field
        :param config: in **kwargs format
        """
        return self._add_field_spec(key, date_iso(**config))

    def date_iso_us(self, key: str, **config):
        """
        creates date.iso.us Field Spec and adds to Data Spec

        :param key: name of ref/field
        :param config: in **kwargs format
        """
        return self._add_field_spec(key, date_iso_us(**config))

    def uuid(self, key: str, **config):
        """
        creates uuid Field Spec and adds to Data Spec

        :param key: name of ref/field
        :param config: in **kwargs format
        """
        return self._add_field_spec(key, uuid(**config))

    def char_class(self, key: str, data: Union[str, List[str]], **config):
        """
        creates char_class Field Spec and adds to Data Spec

        :param key: name of ref/field
        :param data: either known character class or set of characters to use for sampling from
        :param config: in **kwargs format
        """
        return self._add_field_spec(key, char_class(data, **config))

    def char_class_abbrev(self, key: str, cc_abbrev: str, **config):
        """
        creates char_class_abbrev Field Spec and adds to Data Spec

        :param key: name of ref/field
        :param cc_abbrev: alternative type abbreviation i.e. ascii, cc-ascii, visible, cc-visible
        :param config: in **kwargs format
        """
        return self._add_field_spec(key, char_class_abbrev(cc_abbrev, **config))

    def unicode_range(self, key: str, data: Union[List[str], List[List[str]]], **config):
        """
        creates unicode_range Field Spec and adds to Data Spec

        :param key: name of ref/field
        :param data: hex start and end unicode ranges or lists of these
        :param config: in **kwargs format
        """
        return self._add_field_spec(key, unicode_range  (data, **config))

    def geo_lat(self, key: str, **config):
        """
        creates geo.lat Field Spec and adds to Data Spec

        :param key: name of ref/field
        :param config: in **kwargs format
        """
        return self._add_field_spec(key, geo_lat(**config))

    def geo_long(self, key: str, **config):
        """
        creates geo.long Field Spec and adds to Data Spec

        :param key: name of ref/field
        :param config: in **kwargs format
        """
        return self._add_field_spec(key, geo_long(**config))

    def geo_pair(self, key: str, **config):
        """
        creates geo.pair Field Spec and adds to Data Spec

        :param key: name of ref/field
        :param config: in **kwargs format
        """
        return self._add_field_spec(key, geo_pair(**config))

    def ip(self, key: str, **config):
        """
        creates ip Field Spec and adds to Data Spec

        :param key: name of ref/field
        :param config: in **kwargs format
        """
        return self._add_field_spec(key, ip(**config))

    def ipv4(self, key: str, **config):
        """
        creates ipv4 Field Spec and adds to Data Spec

        :param key: name of ref/field
        :param config: in **kwargs format
        """
        return self._add_field_spec(key, ipv4(**config))

    def ip_precise(self, key: str, **config):
        """
        creates ip.precise Field Spec and adds to Data Spec

        :param key: name of ref/field
        :param config: in **kwargs format
        """
        return self._add_field_spec(key, ip_precise(**config))

    def weightedref(self, key: str, data: Dict[str, float], **config):
        """
        creates weightedref Field Spec and adds to Data Spec

        :param key: name of ref/field
        :param data: Mapping of ref name to weight
        :param config: in **kwargs format
        """
        return self._add_field_spec(key, weightedref(data, **config))

    def select_list_subset(self, key: str, data: List[Any] = None, ref: str = None, **config):
        """
        creates select_list_subset Field Spec and adds to Data Spec

        :param key: name of ref/field
        :param data: to select from
        :param ref: that contains data to select from
        :param config: in **kwargs format
        """
        return self._add_field_spec(key, select_list_subset(data, ref, **config))

    def csv(self, key: str, **config):
        """
        creates csv Field Spec and adds to Data Spec

        :param key: name of ref/field
        :param config: in **kwargs format
        """
        return self._add_field_spec(key, csv(**config))

    def csv_select(self, key: str, data: Dict[str, int] = None, **config):
        """
        creates csv_select Field Spec and adds to Data Spec

        :param key: name of ref/field
        :param data: param data: Mapping of field name to one based column number
        :param config: in **kwargs format
        """
        return self._add_field_spec(key, csv_select(data, **config))

    def nested(self, key: str, fields: Dict[str, Dict], **config):
        """
        creates nested Field Spec and adds to Data Spec

        :param key: name of ref/field
        :param fields: sub field specifications
        :param config: in **kwargs format
        """
        return self._add_field_spec(key, nested(fields, **config))

    def _add_field_spec(self, key, spec):
        self.add_field(key, spec)
        return FieldInfo(key, spec['type'], self)

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
            log.warning('%s key already defined, overwriting with %s', key, json.dumps(spec))
        self.keys.add(key)
        self.refs_builder.add_field(key, spec)
        return self

    def weighted_field_group(self, key: str, fields: List[str], weight: float):
        """
        Creates a weighted field group for a single key and add to Spec
        :param key: the name of the field group
        :param fields: the fields in the group
        :param weight: the weight for this group
        :return: FieldInfo
        """
        field_group = {
            key: {
                "weight": weight,
                "fields": fields
            }
        }
        self.field_groups.append(field_group)
        return FieldInfo(key, 'field_group')

    def named_field_group(self, key: str, fields: List[str]):
        """
        Create a named field group for a single key and add to Spec
        :param key: the name of the field group
        :param fields: the fields in the group
        :return: FieldInfo
        """
        field_group = {
            key: fields
        }
        self.field_groups.append(field_group)
        return FieldInfo(key, 'field_group')

    def add_field_groups(self, field_groups: List[Union[List[str], Dict[str, Dict]]]):
        """
        Add a single field group
        :param field_groups: to add
        :return: self for chaining invocations
        """
        for field_group in field_groups:
            self.add_field_group(field_group)
        return self

    def add_field_group(self, field_group: Union[List[str], Dict[str, Dict]]):
        """
        Add a single field group
        :param field_group: to add
        :return: self for chaining invocations
        """
        self.field_groups.append(field_group)
        return self

    def build(self):
        """
        Generates the spec from the provided fields, refs, and field_groups
        :return: The built spec
        """
        spec = {}
        spec.update(self.fields)
        if len(self.refs_builder.fields) > 0:
            spec['refs'] = self.refs_builder.fields
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


def values(data: Union[int, float, str, bool, List, Dict[str, float]], **config):
    """
    Constructs a values Field Spec

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


def combine(refs: List[Union[str, FieldInfo]] = None, fields: List[Union[str, FieldInfo]] = None, **config):
    """
    Constructs a combine Field Spec

    :param refs: refs to combine
    :param fields: fields to combine
    :param config: in **kwargs format
    :return: the combine spec
    """

    spec = {
        "type": "combine"
    }
    if refs is not None:
        spec['refs'] = _create_key_list(refs)
    if fields is not None:
        spec['fields'] = _create_key_list(fields)

    if len(config) > 0:
        spec['config'] = config
    return spec


def combine_list(refs: List[List[Union[str, FieldInfo]]] = None, **config):
    """
    Constructs a combine-list Field Spec

    :param refs: lists of lists of refs to combine
    :param config: in **kwargs format
    :return: the combine-list spec
    """

    spec = {
        "type": "combine-list",
        "refs": [_create_key_list(ref_list) for ref_list in refs]
    }

    if len(config) > 0:
        spec['config'] = config
    return spec


def range_spec(start: Union[int, float], end: Union[int, float], step: Union[int, float], **config):
    """
    Constructs a range Field Spec

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


def rand_range(start: Union[int, float], end: Union[int, float], **config):
    """
    Constructs a rand_range Field Spec

    :param start: start of range inclusive
    :param end: end of range inclusive
    :param config: in **kwargs format
    :return: the rand_range spec
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
    Constructs a date Field Spec

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
    Constructs a date.iso Field Spec

    :param config: in **kwargs format
    :return: the date.iso spec
    """

    spec = {
        "type": "date.iso"
    }

    if len(config) > 0:
        spec['config'] = config
    return spec


def date_iso_us(**config):
    """
    Constructs a date.iso.us Field Spec

    :param config: in **kwargs format
    :return: the date.iso.us spec
    """

    spec = {
        "type": "date.iso.us"
    }

    if len(config) > 0:
        spec['config'] = config
    return spec


def uuid(**config):
    """
    Constructs a uuid Field Spec

    :param config: in **kwargs format
    :return: the uuid spec
    """

    spec = {
        "type": "uuid"
    }

    if len(config) > 0:
        spec['config'] = config
    return spec


def char_class(data: Union[str, List[str]], **config):
    """
    Constructs a char_class Field Spec

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
    spec = {
        "type": 'char_class_abbrev'
    }
    if cc_abbrev.startswith('cc-'):
        spec['type'] = cc_abbrev
    else:
        spec['type'] = 'cc-' + cc_abbrev

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

    if data is not None:
        spec['data'] = data
    if ref is not None:
        spec['ref'] = ref

    if len(config) > 0:
        spec['config'] = config
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

    if data is not None:
        spec['data'] = data

    if len(config) > 0:
        spec['config'] = config
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


def _create_key_list(entries):
    """
    Checks if entries are from FieldInfo objects and extracts keys

    :param entries: to create key list from
    :return: the list of keys
    """
    if len(entries) == 0:
        return []
    if isinstance(entries[0], FieldInfo):
        return [entry.key for entry in entries]
    # this should be a regular list of strings
    return entries
