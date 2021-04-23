#!/bin/env python

import json
import yaml
from collections import OrderedDict
import subprocess

from examples import EXAMPLES


def build_example(spec, iterations=5, pipes=""):
    if pipes is None:
        pipes = ""
    spec_string = json.dumps(spec.raw_spec)
    cmd = f"dataspec --inline '{spec_string}' --log-level error -i {iterations} {pipes}"
    out = subprocess.check_output(cmd, shell=True)
    cmd_display = cmd
    if len(spec_string) > 80:
        cmd_display = f"dataspec -s dataspec.json --log-level error -i {iterations} {pipes}"
    ordered = order_spec(spec.raw_spec)

    example = {
        "json": json.dumps(ordered, cls=MyEncoder, sort_keys=False, indent=2).strip(),
        "yaml": yaml.dump(spec.raw_spec, default_flow_style=False, sort_keys=False).strip(),
        "api": code.strip(),
        "command": cmd_display.strip(),
        "output": out.decode('utf-8').strip()
    }
    return example


def order_spec(raw_spec):
    outer = {}
    for field, spec in raw_spec.items():
        outer[field] = order_field_spec(spec)
    return outer


def order_field_spec(field_spec):
    if not isinstance(field_spec, dict):
        return NoIndent(field_spec)
    ordered = OrderedDict()
    if 'type' in field_spec:
        ordered['type'] = field_spec['type']
    if 'data' in field_spec:
        ordered['data'] = NoIndent(field_spec['data'])
    for key in ['config', 'ref', 'refs', 'fields']:
        if key in field_spec:
            ordered[key] = field_spec[key]
    return ordered

##################################
# from https://stackoverflow.com/questions/13249415/how-to-implement-custom-indentation-when-pretty-printing-with-the-json-module
##################################
from _ctypes import PyObj_FromPtr
import json
import re


class NoIndent(object):
    """ Value wrapper. """

    def __init__(self, value):
        self.value = value


class MyEncoder(json.JSONEncoder):
    FORMAT_SPEC = '@@{}@@'
    regex = re.compile(FORMAT_SPEC.format(r'(\d+)'))

    def __init__(self, **kwargs):
        # Save copy of any keyword argument values needed for use here.
        self.__sort_keys = kwargs.get('sort_keys', None)
        super(MyEncoder, self).__init__(**kwargs)

    def default(self, obj):
        return (self.FORMAT_SPEC.format(id(obj)) if isinstance(obj, NoIndent)
                else super(MyEncoder, self).default(obj))

    def encode(self, obj):
        format_spec = self.FORMAT_SPEC  # Local var to expedite access.
        json_repr = super(MyEncoder, self).encode(obj)  # Default JSON.

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


template = """
import dataspec

spec_builder = dataspec.spec_builder()

FRAGMENT

spec = spec_builder.build()
"""

built_examples = {}
for name, iterations, fragment, pipes in EXAMPLES:
    code = template.replace('FRAGMENT', fragment)
    try:
        exec(code)
        data = build_example(spec, iterations, pipes)
        built_examples[name] = data
    except TypeError as err:
        print(err)
        print(name)
        print(code)
        raise Exception() from err
        #exit(-1)
    # spec should be created when running exec

print(json.dumps({"examples": built_examples}, cls=MyEncoder, sort_keys=False, indent=2))
