"""
Module with functions that handle formatting specs in an orderly and consistent structure i.e:

.. code-block:: json

  {
    "type": "<type name>",
    "data": "data stuff",
    "refs": "refs pointers",
    "config": {
      "key": "value..."
    }
  }
"""
import logging
from collections import OrderedDict

import yaml

_log = logging.getLogger('spec.formatter')


def format_json(raw_spec: dict) -> str:
    """
    Formats the raw_spec as ordered dictionary in JSON

    Args:
        raw_spec: to format

    Returns:
        the ordered and formatted JSON string
    """
    ordered = _order_spec(raw_spec)
    return json.dumps(ordered, cls=_MyEncoder, sort_keys=False, indent=2).strip()


def format_yaml(raw_spec: dict) -> str:
    """
    Formats the raw_spec as ordered dictionary in YAML

    Args:
        raw_spec: to format

    Returns:
        the ordered and formatted YAML string
    """
    ordered = _order_spec(raw_spec)
    dirty_yaml = yaml.dump(ordered, sort_keys=False, width=4096).strip()
    cleaned_yaml = _clean_semi_formatted_yaml(dirty_yaml)
    try:
        loaded_yaml = yaml.load(cleaned_yaml, Loader=yaml.FullLoader)
        if loaded_yaml != raw_spec:
            _log.warning('yaml does not match raw')
            _log.warning(json.dumps(loaded_yaml, indent=4))
            _log.warning(json.dumps(raw_spec, indent=4))
    except Exception:
        _log.warning('yaml does not load')
        _log.warning(cleaned_yaml)
        _log.warning(dirty_yaml)
    return cleaned_yaml


def _clean_semi_formatted_yaml(toclean: str):
    """
    Our custom YAML formatter adds a bunch of stuff we need to clean up since it is working with
    and OrderdDict as the underlying structure.
    """
    return toclean.replace('!!list ', '')


def _order_spec(raw_spec):
    outer = {}
    for field, spec in raw_spec.items():
        if field == 'refs':
            continue
        outer[field] = _order_field_spec(spec)
    if 'refs' in raw_spec:
        updated_refs = {}
        for ref, spec in raw_spec['refs'].items():
            updated_refs[ref] = _order_field_spec(spec)
        outer['refs'] = updated_refs
    return outer


def _order_field_spec(field_spec):
    if not isinstance(field_spec, dict):
        return _NoIndent(field_spec)
    ordered = OrderedDict()
    if 'type' in field_spec:
        ordered['type'] = field_spec['type']
    if 'data' in field_spec:
        ordered['data'] = _NoIndent(field_spec['data'])
    if 'refs' in field_spec:
        refs = field_spec['refs']
        if isinstance(refs, list) and isinstance(refs[0], list):
            ordered['refs'] = [_NoIndent(ref) for ref in refs]
        else:
            ordered['refs'] = _NoIndent(refs)
    for key in ['config', 'ref', 'fields']:
        if key in field_spec:
            ordered[key] = field_spec[key]
    for key, val in field_spec.items():
        if key not in ['type', 'data', 'config', 'ref', 'refs', 'fields']:
            ordered[key] = val
    return ordered


##################################
# from https://stackoverflow.com/questions/13249415/how-to-implement-custom-indentation-when-pretty-printing-with-the-json-module
##################################
from _ctypes import PyObj_FromPtr  # type: ignore
import json
import re


class _NoIndent(object):
    """ Value wrapper. """

    def __init__(self, value):
        self.value = value

    @classmethod
    def to_yaml(cls, representer, node):
        """
        Added to support formatting for YAML
        """
        return representer.represent_scalar(' ', u'{.value}'.format(node))


class _MyEncoder(json.JSONEncoder):
    FORMAT_SPEC = '@@{}@@'
    regex = re.compile(FORMAT_SPEC.format(r'(\d+)'))

    def __init__(self, **kwargs):
        # Save copy of any keyword argument values needed for use here.
        self.__sort_keys = kwargs.get('sort_keys', None)
        super(_MyEncoder, self).__init__(**kwargs)

    def default(self, obj):
        return (self.FORMAT_SPEC.format(id(obj)) if isinstance(obj, _NoIndent)
                else super(_MyEncoder, self).default(obj))

    def encode(self, obj):
        format_spec = self.FORMAT_SPEC  # Local var to expedite access.
        json_repr = super(_MyEncoder, self).encode(obj)  # Default JSON.

        # Replace any marked-up object ids in the JSON repr with the
        # value returned from the json.dumps() of the corresponding
        # wrapped Python object.
        for match in self.regex.finditer(json_repr):
            # see https://stackoverflow.com/a/15012814/355230
            id = int(match.group(1))
            no_indent = PyObj_FromPtr(id)
            json_obj_repr = json.dumps(no_indent.value, sort_keys=self.__sort_keys)

            # Replace the matched id string with json formatted representation
            # of the corresponding Python object.
            json_repr = json_repr.replace(
                '"{}"'.format(format_spec.format(id)), json_obj_repr)

        return json_repr


#########################
# from https://til.simonwillison.net/python/style-yaml-dump
# via: https://stackoverflow.com/a/8641732 and https://stackoverflow.com/a/16782282
#########################
def _represent_ordered_dict(dumper, data):
    value = []

    for item_key, item_value in data.items():
        node_key = dumper.represent_data(item_key)
        node_value = dumper.represent_data(item_value)

        value.append((node_key, node_value))

    return yaml.nodes.MappingNode(u"tag:yaml.org,2002:map", value)


yaml.add_representer(OrderedDict, _represent_ordered_dict)


def _represent_noindent(dumper, data):
    if isinstance(data.value, list):
        return dumper.represent_sequence("tag:yaml.org,2002:list", data.value, flow_style=True)
    if isinstance(data.value, dict):
        return dumper.represent_mapping("tag:yaml.org,2002:map", data.value, flow_style=True)
    return dumper.represent_data(data.value)


yaml.add_representer(_NoIndent, _represent_noindent)
