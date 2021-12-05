"""
Module for building Data Specs programmatically.

Examples:
    >>> import datagen
    >>> builder = datagen.spec_builder()
    >>> builder.values('names', ['amy', 'bob', 'cat','dan'])
    >>> builder.range_spec('ages', data=[22, 33])
    {'names': {'type': 'values', 'data': ['amy', 'bob', 'cat', 'dan']}, 'ages': {'type': 'range', 'data': [22, 33]}}

    >>> refs = spec_builder.refs()
    >>> one = refs.values('ONE', ["A", "B", "C"])
    >>> two = refs.values('TWO', [1, 2, 3])
    >>> builder.combine('combine', refs=[one, two])
    >>> builder.build()
    {'combine': {'type': 'combine', 'refs': ['ONE', 'TWO']}, 'refs': {'ONE': {'type': 'values', 'data': ['A', 'B', 'C']}
    , 'TWO': {'type': 'values', 'data': [1, 2, 3]}}}
"""
import json
import logging
from typing import Any, Union, Dict, List
from typing import Generator

from . import registries, utils
from .loader import Loader, preprocess_spec
from .supplier import key_suppliers
from .supplier.model import DataSpec

_log = logging.getLogger(__name__)


class FieldInfo:
    """
    Class for holding info after adding field or ref to spec. Can be passed to specs that use other specs
    like combine
    """

    def __init__(self, key: str, type_name: str, builder=None):
        self.key = key
        self.type_name = type_name
        self.builder = builder

    def to_spec(self) -> DataSpec:
        """
        Builds the Data Spec from the underlying builder

        Returns:
            the Data Spec
        """
        return self.builder.build()


class Builder:
    """
    Container class for constructing the Data Spec by adding fields, refs, and field_groups
    """

    def __init__(self, has_refs=True):
        if has_refs:
            self.refs_builder = Builder(False)
        else:
            self.refs_builder = None
        self.fields = {}
        self.field_groups = []
        self.keys = set()

    def refs(self):
        """
        Get Refs object for this builder

        Returns:
            the refs builder which is itself also a builder
        """
        return self.refs_builder

    def values(self, key: str,
               data: Union[int, float, str, bool, List, Dict[str, float]],
               **config) -> FieldInfo:
        """
        creates values Field Spec and adds to Data Spec

        Args:
            key: name of ref/field
            data: to use to supply values
            config: in kwargs format

        Returns:
            FieldInfo for the added values field
        """
        return self._add_field_spec(key, values(data, **config))

    def combine(self, key: str,
                refs: Union[List[str], List[FieldInfo]] = None,
                fields: Union[List[str], List[FieldInfo]] = None,
                **config) -> FieldInfo:
        """
        creates combine Field Spec and adds to Data Spec

        Args:
            key: name of ref/field
            refs: refs to combine
            fields: fields to combine
            config: in kwargs format

        Returns:
            FieldInfo for the added combine field
        """
        return self._add_field_spec(key, combine(refs, fields, **config))

    def combine_list(self, key: str,
                     refs: List[Union[List[str], List[FieldInfo]]] = None,
                     **config) -> FieldInfo:
        """
        creates combine-list Field Spec and adds to Data Spec

        Args:
            key: name of ref/field
            refs: lists of lists of refs to combine
            config: in kwargs format

        Returns:
            FieldInfo for the added combine-list field
        """
        return self._add_field_spec(key, combine_list(refs, **config))

    def range_spec(self, key: str, data: list, **config) -> FieldInfo:
        """
        creates range Field Spec and adds to Data Spec

        Args:
            key: name of ref/field
            data: with start, end, and optional step
            config: in kwargs format

        Returns:
            FieldInfo for the added range field
        """
        return self._add_field_spec(key, range_spec(data, **config))

    def rand_range(self, key: str, data: list, **config) -> FieldInfo:
        """
        creates rand_range Field Spec and adds to Data Spec

        Args:
            key: name of ref/field
            data: with start and end of ranges
            config: in kwargs format

        Returns:
            FieldInfo for the added rand_range field
        """
        return self._add_field_spec(key, rand_range(data, **config))

    def date(self, key: str, **config) -> FieldInfo:
        """
        creates date Field Spec and adds to Data Spec

        Args:
            key: name of ref/field
            config: in kwargs format

        Returns:
            FieldInfo for the added date field
        """
        return self._add_field_spec(key, date(**config))

    def date_iso(self, key: str, **config) -> FieldInfo:
        """
        creates date.iso Field Spec and adds to Data Spec

        Args:
            key: name of ref/field
            config: in kwargs format

        Returns:
            FieldInfo for the added date.iso field
        """
        return self._add_field_spec(key, date_iso(**config))

    def date_iso_us(self, key: str, **config) -> FieldInfo:
        """
        creates date.iso.us Field Spec and adds to Data Spec

        Args:
            key: name of ref/field
            config: in kwargs format

        Returns:
            FieldInfo for the added date.iso.us field
        """
        return self._add_field_spec(key, date_iso_us(**config))

    def uuid(self, key: str, **config) -> FieldInfo:
        """
        creates uuid Field Spec and adds to Data Spec

        Args:
            key: name of ref/field
            config: in kwargs format

        Returns:
            FieldInfo for the added uuid field
        """
        return self._add_field_spec(key, uuid(**config))

    def char_class(self, key: str, data: Union[str, List[str]], **config) -> FieldInfo:
        """
        creates char_class Field Spec and adds to Data Spec

        Args:
            key: name of ref/field
            data: either known character class or set of characters to use for sampling from
            config: in kwargs format

        Returns:
            FieldInfo for the added char_class field
        """
        return self._add_field_spec(key, char_class(data, **config))

    def char_class_abbrev(self, key: str, cc_abbrev: str, **config) -> FieldInfo:
        """
        creates char_class_abbrev Field Spec and adds to Data Spec

        Args:
            key: name of ref/field
            cc_abbrev: alternative type abbreviation i.e. ascii, cc-ascii, visible, cc-visible
            config: in kwargs format

        Returns:
            FieldInfo for the added char_class_abbrev field
        """
        return self._add_field_spec(key, char_class_abbrev(cc_abbrev, **config))

    def unicode_range(self, key: str, data: Union[List[str], List[List[str]]], **config) -> FieldInfo:
        """
        creates unicode_range Field Spec and adds to Data Spec

        Args:
            key: name of ref/field
            data: hex start and end unicode ranges or lists of these
            config: in kwargs format

        Returns:
            FieldInfo for the added unicode_range field
        """
        return self._add_field_spec(key, unicode_range(data, **config))

    def geo_lat(self, key: str, **config) -> FieldInfo:
        """
        creates geo.lat Field Spec and adds to Data Spec

        Args:
            key: name of ref/field
            config: in kwargs format

        Returns:
            FieldInfo for the added geo.lat field
        """
        return self._add_field_spec(key, geo_lat(**config))

    def geo_long(self, key: str, **config) -> FieldInfo:
        """
        creates geo.long Field Spec and adds to Data Spec

        Args:
            key: name of ref/field
            config: in kwargs format

        Returns:
            FieldInfo for the added geo.long field
        """
        return self._add_field_spec(key, geo_long(**config))

    def geo_pair(self, key: str, **config) -> FieldInfo:
        """
        creates geo.pair Field Spec and adds to Data Spec

        Args:
            key: name of ref/field
            config: in kwargs format

        Returns:
            FieldInfo for the added geo.pair field
        """
        return self._add_field_spec(key, geo_pair(**config))

    def ip(self, key: str, **config) -> FieldInfo:
        """
        creates ip Field Spec and adds to Data Spec

        Args:
            key: name of ref/field
            config: in kwargs format

        Returns:
            FieldInfo for the added ip field
        """
        return self._add_field_spec(key, ip(**config))

    def ipv4(self, key: str, **config) -> FieldInfo:
        """
        creates ipv4 Field Spec and adds to Data Spec

        Args:
            key: name of ref/field
            config: in kwargs format

        Returns:
            FieldInfo for the added ipv4 field
        """
        return self._add_field_spec(key, ipv4(**config))

    def ip_precise(self, key: str, **config) -> FieldInfo:
        """
        creates ip.precise Field Spec and adds to Data Spec

        Args:
            key: name of ref/field
            config: in kwargs format

        Returns:
            FieldInfo for the added ip.precise field
        """
        return self._add_field_spec(key, ip_precise(**config))

    def mac(self, key: str, **config) -> FieldInfo:
        """
        creates net.mac Field Spec and adds to Data Spec

        Args:
            key: name of ref/field
            config: in kwargs format

        Returns:
            FieldInfo for the added net.mac field
        """
        return self._add_field_spec(key, mac(**config))

    def weighted_ref(self, key: str, data: Dict[str, float], **config) -> FieldInfo:
        """
        creates weighted_ref Field Spec and adds to Data Spec

        Args:
            key: name of ref/field
            data: Mapping of ref name to weight
            config: in kwargs format

        Returns:
            FieldInfo for the added weighted_ref field
        """
        return self._add_field_spec(key, weighted_ref(data, **config))

    def select_list_subset(self, key: str, data: List[Any] = None, ref_name: str = None, **config) -> FieldInfo:
        """
        creates select_list_subset Field Spec and adds to Data Spec

        Args:
            key: name of ref/field
            data: to select from
            ref_name: that contains data to select from
            config: in kwargs format

        Returns:
            FieldInfo for the added select_list_subset field
        """
        return self._add_field_spec(key, select_list_subset(data, ref_name, **config))

    def csv(self, key: str, **config) -> FieldInfo:
        """
        creates csv Field Spec and adds to Data Spec

        Args:
            key: name of ref/field
            config: in kwargs format

        Returns:
            FieldInfo for the added csv field
        """
        return self._add_field_spec(key, csv(**config))

    def csv_select(self, key: str, data: Dict[str, int] = None, **config) -> FieldInfo:
        """
        creates csv_select Field Spec and adds to Data Spec

        Args:
            key: name of ref/field
            data: Mapping of field name to one based column number
            config: in kwargs format

        Returns:
            FieldInfo for the added csv_select field
        """
        return self._add_field_spec(key, csv_select(data, **config))

    def nested(self, key: str, fields: Union[Dict[str, Dict], DataSpec], **config) -> FieldInfo:
        """
        creates nested Field Spec and adds to Data Spec

        Args:
            key: name of ref/field
            fields: sub field specifications
            config: in kwargs format

        Returns:
            FieldInfo for the added nested field
        """
        return self._add_field_spec(key, nested(fields, **config))

    def config_ref(self, key: str, **config):
        """
        creates config_ref Field Spec and adds to Data Spec

        Args:
            key: name of ref/field
            config: in kwargs format

        Returns:
            FieldInfo for the added config_ref field
        """
        # this must be a refs instance
        if self.refs_builder is None:
            return self._add_field_spec(key, config_ref(**config))
        return self.add_ref(key, config_ref(**config))

    def calculate(self, key: str,
                  refs: dict = None,
                  fields: dict = None,
                  formula: str = None,
                  **config) -> FieldInfo:
        """
        creates calculate Field Spec and adds to Data Spec

        Args:
            key: name of ref/field
            refs: mapping of ref to alias to used in formula
            fields: mapping of field name to alias used in formula
            formula: formula to execute against results of refs/fields
            config: in kwargs format

        Returns:
            FieldInfo for the added calculate field
        """
        return self._add_field_spec(key, calculate(refs, fields, formula, **config))

    def ref(self, key: str, ref_name: str = None, data: str = None, **config) -> FieldInfo:
        """
        creates ref Field Spec and adds to Data Spec

        Args:
            key: name of ref/field
            ref_name: name of reference to get values from
            data: name of reference to get values from
            config: in kwargs format

        Returns:
            FieldInfo for the added ref field
        """
        return self._add_field_spec(key, ref_spec(ref_name, data, **config))

    def weighted_csv(self, key: str, **config) -> FieldInfo:
        """
        creates weighted_csv Field Spec and adds to Data Spec

        Args:
            key: name of ref/field
            config: in kwargs format

        Returns:
            FieldInfo for the added weighted_csv field
        """
        return self._add_field_spec(key, weighted_csv(**config))

    def distribution(self, key: str, data: str, **config) -> FieldInfo:
        """
        creates distribution Field Spec and adds to Data Spec

        Args:
            key: name of ref/field
            data: formula for distribution if func(param=val, ...) format
            config: in kwargs format

        Returns:
            FieldInfo for the added distribution field
        """
        return self._add_field_spec(key, distribution(data, **config))

    def _add_field_spec(self, key, spec) -> FieldInfo:
        """
        adds the fieldspec and creates a FieldInfo object

        Args:
            key: key for field
            spec: to add

        Returns:
            FieldInfo for key and spec
        """
        self.add_field(key, spec)
        return FieldInfo(key, spec['type'], self)

    def add_fields(self, **kwargs):
        """
        Add all fields to the spec. See examples for formatting.

        Args:
            **kwargs: where key is field name and value is a generated spec

        Returns:
            self for chaining invocations

        Examples:
            >>> builder = datagen.spec_buider()
            >>> builder.add_fields(FIELDNAME1=builder.some_spec(with_args), FIELDNAME2=builder.another_spec(with_args)
        )
        """
        for key, spec in kwargs.items():
            self.add_field(key, spec)
        return self

    def add_field(self, key: Union[str, FieldInfo], spec: dict):
        """
        Add single field to the spec.

        Args:
            key: field name
            spec: the generate spec for this field

        Returns:
            self for chaining invocations

        Examples:
            >>> builder = datagen.spec_buider()
            >>> builder.add_field("field1", builder.some_spec(with_args))
            >>> builder.add_field("field2", builder.another_spec(with_args))
        """
        if key in self.keys:
            _log.warning('%s key already defined, overwriting with %s',
                         key, json.dumps(spec))
        if isinstance(key, FieldInfo):
            key = key.key
        self.keys.add(key)
        self.fields[key] = spec
        return self

    def add_refs(self, **kwargs):
        """
        Add all refs to the spec. See Examples for format.

        Args:
            **kwargs: where key is ref name and value is a generated spec

        Returns:
            self for chaining invocations

        Examples:
            >>> builder = datagen.spec_buider()
            >>> builder.add_refs(
            ...     REFNAME1=builder.some_spec(with_args),
            ...     REFNAME2=builder.another_spec(with_args))
        """
        for key, spec in kwargs.items():
            self.add_ref(key, spec)
        return self

    def add_ref(self, key: str, spec: dict):
        """
        Add single ref to the spec.

        Args:
            key: ref name
            spec: the generate spec for this ref

        Returns:
            self for chaining invocations

        Examples:
            >>> builder = datagen.spec_builder()
            >>> builder.add_ref("ref1", builder.some_spec(with_args))
            >>> builder.add_ref("ref2", builder.another_spec(with_args))
        """
        if key in self.keys:
            _log.warning('%s key already defined, overwriting with %s', key, json.dumps(spec))
        self.keys.add(key)
        self.refs_builder.add_field(key, spec)
        return self

    def weighted_field_group(self, weight: float, fields: List[str]):
        """
        Creates a weighted field group for a single key and add to Spec

        Args:
            fields: the fields in the group
            weight: the weight for this group

        Returns:
            FieldInfo for field group

        Examples:
            >>> import datagen
            >>> builder = datagen.spec_builder()
            >>> builder.weighted_field_group(0.6, ['name', 'age', 'gender'])
            >>> builder.weighted_field_group(0.4, ['name', 'age'])
        """
        field_group = {
            str(weight): fields
        }
        self.field_groups.append(field_group)
        return FieldInfo(str(weight), 'field_group')

    def named_field_group(self, key: str, fields: List[str]):
        """
        Create a named field group for a single key and add to Spec

        Args:
            key: the name of the field group
            fields: the fields in the group

        Returns:
            FieldInfo

        Examples:
            >>> import datagen
            >>> builder = datagen.spec_builder()
            >>> builder.named_field_group("all", ['name', 'age', 'gender'])
            >>> builder.named_field_group("no_gender", ['name', 'age'])
        """
        field_group = {
            key: fields
        }
        self.field_groups.append(field_group)
        return FieldInfo(key, 'field_group')

    def add_field_groups(self, field_groups: List[Union[List[str], Dict[str, Dict]]]):
        """
        Add a single field group

        Args:
            field_groups: to add

        Returns:
            self for chaining invocations
        """
        for field_group in field_groups:
            self.add_field_group(field_group)
        return self

    def add_field_group(self, field_group: Union[List[str], Dict[str, Dict]]):
        """
        Add a single field group

        Args:
            field_group: to add

        Returns:
            self for chaining invocations
        """
        self.field_groups.append(field_group)
        return self

    def build(self) -> DataSpec:
        """
        Generates the spec from the provided fields, refs, and field_groups

        Returns:
            Built DataSpec
        """
        spec = {}
        spec.update(self.fields)
        if len(self.refs_builder.fields) > 0:
            spec['refs'] = self.refs_builder.fields
        if len(self.field_groups) > 0:
            self._configure_field_groups(spec)

        return _DataSpecImpl(spec)

    def _configure_field_groups(self, spec: dict):
        """
        Adds the field_groups element to the spec if needed and defined"""
        all_dict = all(isinstance(entry, dict) for entry in self.field_groups)
        if all_dict:
            flattened = {}
            for entry in self.field_groups:
                flattened.update(entry)
            spec['field_groups'] = flattened
        all_list = all(isinstance(entry, list) for entry in self.field_groups)
        if all_list:
            spec['field_groups'] = self.field_groups


def parse_spec(raw_spec: dict) -> DataSpec:
    """
    Parses the raw spec into a DataSpec object. Takes in specs that may contain shorthand specifications.

    Args:
        raw_spec: raw dictionary that conforms to JSON spec format

    Returns:
        the fully parsed and loaded spec
    """
    specs = preprocess_spec(raw_spec)
    return _DataSpecImpl(specs)


def spec_builder() -> Builder:
    """
    Creates a new DataSpec builder

    Returns:
        the Builder()
    """
    return Builder()


def single_field(name: str, spec: dict) -> Builder:
    """
    Creates Builder for single field and spec

    Args:
        name: of field
        spec: for field

    Returns:
        Builder with single field populated
    """
    return Builder().add_field(name, spec)


def values(data: Union[int, float, str, bool, List, Dict[str, float]], **config) -> dict:
    """
    Constructs a values Field Spec

    Args:
        data: to use to supply values
        config: in kwargs format

    Returns:
        the values spec
    """

    spec = {
        "type": "values",
        "data": data
    }  # type: Dict[str, Any]

    if len(config) > 0:
        spec['config'] = config
    return spec


def combine(refs: Union[List[str], List[FieldInfo]] = None,
            fields: Union[List[str], List[FieldInfo]] = None,
            **config) -> dict:
    """
    Constructs a combine Field Spec

    Args:
        refs: refs to combine
        fields: fields to combine
        config: in kwargs format

    Returns:
        the combine spec
    """

    spec = {
        "type": "combine"
    }  # type: Dict[str, Any]
    if refs is not None:
        spec['refs'] = _create_key_list(refs)
    if fields is not None:
        spec['fields'] = _create_key_list(fields)

    if len(config) > 0:
        spec['config'] = config
    return spec


def combine_list(refs: List[Union[List[str], List[FieldInfo]]] = None, **config) -> dict:
    """
    Constructs a combine-list Field Spec

    Args:
        refs: lists of lists of refs to combine
        config: in kwargs format

    Returns:
        the combine-list spec
    """
    if refs is None:
        refs = []
    spec = {
        "type": "combine-list",
        "refs": [_create_key_list(ref_list) for ref_list in refs]
    }  # type: Dict[str, Any]

    if len(config) > 0:
        spec['config'] = config
    return spec


def range_spec(data: list, **config) -> dict:
    """
    Constructs a range Field Spec

    Args:
        data: with start, end, and optional step
        config: in kwargs format

    Returns:
        the range spec
    """

    spec = {
        "type": "range",
        "data": data
    }  # type: Dict[str, Any]

    if len(config) > 0:
        spec['config'] = config
    return spec


def rand_range(data: list, **config) -> dict:
    """
    Constructs a rand_range Field Spec

    Args:
        data: with start and end of ranges
        config: in kwargs format

    Returns:
        the rand_range spec
    """

    spec = {
        "type": "rand_range",
        "data": data
    }  # type: Dict[str, Any]

    if len(config) > 0:
        spec['config'] = config
    return spec


def date(**config) -> dict:
    """
    Constructs a date Field Spec

    Args:
        config: in kwargs format

    Returns:
        the date spec
    """

    spec = {
        "type": "date"
    }  # type: Dict[str, Any]

    if len(config) > 0:
        spec['config'] = config
    return spec


def date_iso(**config) -> dict:
    """
    Constructs a date.iso Field Spec

    Args:
        config: in kwargs format

    Returns:
        the date.iso spec
    """

    spec = {
        "type": "date.iso"
    }  # type: Dict[str, Any]

    if len(config) > 0:
        spec['config'] = config
    return spec


def date_iso_us(**config) -> dict:
    """
    Constructs a date.iso.us Field Spec

    Args:
        config: in kwargs format

    Returns:
        the date.iso.us spec
    """

    spec = {
        "type": "date.iso.us"
    }  # type: Dict[str, Any]

    if len(config) > 0:
        spec['config'] = config
    return spec


def uuid(**config) -> dict:
    """
    Constructs a uuid Field Spec

    Args:
        config: in kwargs format

    Returns:
        the uuid spec
    """

    spec = {
        "type": "uuid"
    }  # type: Dict[str, Any]

    if len(config) > 0:
        spec['config'] = config
    return spec


def char_class(data: Union[str, List[str]], **config) -> dict:
    """
    Constructs a char_class Field Spec

    Args:
        data: either known character class or set of characters to use for sampling from
        config: in kwargs format

    Returns:
        the char_class spec
    """

    spec = {
        "type": "char_class",
        "data": data
    }  # type: Dict[str, Any]

    if len(config) > 0:
        spec['config'] = config
    return spec


def char_class_abbrev(cc_abbrev: str, **config) -> dict:
    """
    Constructs a char_class_abbrev Field Spec

    Args:
        cc_abbrev: alternative type abbreviation i.e. ascii, cc-ascii, visible, cc-visible
        config: in kwargs format

    Returns:
        the char_class_abbrev spec
    """

    spec = {
        "type": "char_class_abbrev"
    }  # type: Dict[str, Any]
    if cc_abbrev.startswith('cc-'):
        spec['type'] = cc_abbrev
    else:
        spec['type'] = 'cc-' + cc_abbrev

    if len(config) > 0:
        spec['config'] = config
    return spec


def unicode_range(data: Union[List[str], List[List[str]]], **config) -> dict:
    """
    Constructs a unicode_range Field Spec

    Args:
        data: hex start and end unicode ranges or lists of these
        config: in kwargs format

    Returns:
        the unicode_range spec
    """

    spec = {
        "type": "unicode_range",
        "data": data
    }  # type: Dict[str, Any]

    if len(config) > 0:
        spec['config'] = config
    return spec


def geo_lat(**config) -> dict:
    """
    Constructs a geo.lat Field Spec

    Args:
        config: in kwargs format

    Returns:
        the geo.lat spec
    """

    spec = {
        "type": "geo.lat"
    }  # type: Dict[str, Any]

    if len(config) > 0:
        spec['config'] = config
    return spec


def geo_long(**config) -> dict:
    """
    Constructs a geo.long Field Spec

    Args:
        config: in kwargs format

    Returns:
        the geo.long spec
    """

    spec = {
        "type": "geo.long"
    }  # type: Dict[str, Any]

    if len(config) > 0:
        spec['config'] = config
    return spec


def geo_pair(**config) -> dict:
    """
    Constructs a geo.pair Field Spec

    Args:
        config: in kwargs format

    Returns:
        the geo.pair spec
    """

    spec = {
        "type": "geo.pair"
    }  # type: Dict[str, Any]

    if len(config) > 0:
        spec['config'] = config
    return spec


def ip(**config) -> dict:
    """
    Constructs a ip Field Spec

    Args:
        config: in kwargs format

    Returns:
        the ip spec
    """

    spec = {
        "type": "ip"
    }  # type: Dict[str, Any]

    if len(config) > 0:
        spec['config'] = config
    return spec


def ipv4(**config) -> dict:
    """
    Constructs a ipv4 Field Spec

    Args:
        config: in kwargs format

    Returns:
        the ipv4 spec
    """

    spec = {
        "type": "ipv4"
    }  # type: Dict[str, Any]

    if len(config) > 0:
        spec['config'] = config
    return spec


def ip_precise(**config) -> dict:
    """
    Constructs a ip.precise Field Spec

    Args:
        config: in kwargs format

    Returns:
        the ip.precise spec
    """

    spec = {
        "type": "ip.precise"
    }  # type: Dict[str, Any]

    if len(config) > 0:
        spec['config'] = config
    return spec


def mac(**config) -> dict:
    """
    Constructs a mac Field Spec

    Args:
        config: in kwargs format

    Returns:
        the mac spec
    """

    spec = {
        "type": "net.mac"
    }  # type: Dict[str, Any]

    if len(config) > 0:
        spec['config'] = config
    return spec


def weighted_ref(data: Dict[str, float], **config) -> dict:
    """
    Constructs a weighted_ref Field Spec

    Args:
        data: Mapping of ref name to weight
        config: in kwargs format

    Returns:
        the weighted_ref spec
    """

    spec = {
        "type": "weighted_ref",
        "data": data
    }  # type: Dict[str, Any]

    if len(config) > 0:
        spec['config'] = config
    return spec


def select_list_subset(data: List[Any] = None, ref: str = None, **config) -> dict:
    """
    Constructs a select_list_subset Field Spec

    Args:
        data: to select from
        ref: that contains data to select from
        config: in kwargs format

    Returns:
        the select_list_subset spec
    """

    spec = {
        "type": "select_list_subset"
    }  # type: Dict[str, Any]
    if data is not None:
        spec['data'] = data
    if ref is not None:
        spec['ref'] = ref

    if len(config) > 0:
        spec['config'] = config
    return spec


def csv(**config) -> dict:
    """
    Constructs a csv Field Spec

    Args:
        config: in kwargs format

    Returns:
        the csv spec
    """

    spec = {
        "type": "csv"
    }  # type: Dict[str, Any]

    if len(config) > 0:
        spec['config'] = config
    return spec


def csv_select(data: Dict[str, int] = None, **config) -> dict:
    """
    Constructs a csv_select Field Spec

    Args:
        data: Mapping of field name to one based column number
        config: in kwargs format

    Returns:
        the csv_select spec
    """

    spec = {
        "type": "csv_select"
    }  # type: Dict[str, Any]
    if data is not None:
        spec['data'] = data

    if len(config) > 0:
        spec['config'] = config
    return spec


def nested(fields: Union[Dict[str, Dict], DataSpec], **config) -> dict:
    """
    Constructs a nested Field Spec

    Args:
        fields: sub field specifications
        config: in kwargs format

    Returns:
        the nested spec
    """

    spec = {
        "type": "nested",
        "fields": utils.get_raw_spec(fields)
    }  # type: Dict[str, Any]

    if len(config) > 0:
        spec['config'] = config
    return spec


def config_ref(**config) -> dict:
    """
    Constructs a config_ref Field Spec

    Args:
        config: in kwargs format

    Returns:
        the config_ref spec
    """

    spec = {
        "type": "config_ref"
    }  # type: Dict[str, Any]

    if len(config) > 0:
        spec['config'] = config
    return spec


def calculate(refs: dict = None,
              fields: dict = None,
              formula: str = None,
              **config) -> dict:
    """
    Constructs a calculate Field Spec

    Args:
        refs: mapping of ref to alias to used in formula
        fields: mapping of field name to alias used in formula
        formula: formula to execute against results of refs/fields
        config: in kwargs format

    Returns:
        the calculate spec
    """

    spec = {
        "type": "calculate",
        "formula": formula
    }  # type: Dict[str, Any]
    if refs is not None:
        spec['refs'] = refs
    if fields is not None:
        spec['fields'] = fields

    if len(config) > 0:
        spec['config'] = config
    return spec


def ref_spec(ref_name: str = None, data: str = None, **config) -> dict:
    """
    Constructs a ref Field Spec

    Args:
        ref_name: name of reference to get values from
        data: name of reference to get values from
        config: in kwargs format

    Returns:
        the ref spec
    """

    spec = {
        "type": "ref"
    }  # type: Dict[str, Any]
    if data is not None:
        spec['data'] = data
    if ref_name is not None:
        spec['ref'] = ref_name

    if len(config) > 0:
        spec['config'] = config
    return spec


def weighted_csv(**config) -> dict:
    """
    Constructs a weighted_csv Field Spec

    Args:
        config: in kwargs format

    Returns:
        the weighted_csv spec
    """

    spec = {
        "type": "weighted_csv"
    }  # type: Dict[str, Any]

    if len(config) > 0:
        spec['config'] = config
    return spec


def distribution(data: str = None, **config) -> dict:
    """
    Constructs a distribution Field Spec

    Args:
        data: distribution formula
        config: in kwargs format

    Returns:
        the distribution spec
    """

    spec = {
        "type": "distribution",
        "data": data
    }  # type: Dict[str, Any]

    if len(config) > 0:
        spec['config'] = config
    return spec


def _create_key_list(entries):
    """
    Checks if entries are from FieldInfo objects and extracts keys

    Args:
        entries: to create key list from

    Returns:
        the list of keys
    """
    if len(entries) == 0:
        return []
    if all(isinstance(entry, FieldInfo) for entry in entries):
        return [entry.key for entry in entries]
    # this should be a regular list of strings
    return entries


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
    return _DataSpecImpl(raw_spec).generator(iterations, **kwargs)


class _DataSpecImpl(DataSpec):
    """ Implementation for DataSpec """

    def generator(self, iterations: int, **kwargs):
        processor = kwargs.get('processor')
        data_dir = kwargs.get('data_dir', registries.get_default('data_dir'))
        enforce_schema = kwargs.get('enforce_schema', False)
        exclude_internal = kwargs.get('exclude_internal', False)
        output = kwargs.get('output', None)
        loader = Loader(self.raw_spec, data_dir=data_dir, enforce_schema=enforce_schema)

        key_provider = key_suppliers.from_spec(loader.specs)

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

            if processor is not None:
                yield processor.process(record)
            else:
                yield record
