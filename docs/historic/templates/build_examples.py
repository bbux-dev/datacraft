#!/bin/env python
import os
import json
import logging
import yaml
import subprocess
import argparse

from datagen import spec_formatters

from examples import EXAMPLES

logging.basicConfig(level=logging.INFO)
log = logging.getLogger('example')

template = """
import datagen

spec_builder = datagen.spec_builder()

FRAGMENT

spec = spec_builder.build()
"""


def build_example(name, spec, iterations=5, pipes=""):
    if pipes is None:
        pipes = ""
    with open('dataspec.json', 'w') as handle:
        json.dump(spec.raw_spec, handle)
    spec_string = json.dumps(spec.raw_spec)
    # cmd = f"datagen --inline \"{spec_string}\" --log-level error -i {iterations} {pipes}"
    cmd = f"datagen -s dataspec.json --log-level error -i {iterations} {pipes}"
    log.info(cmd)
    out = subprocess.check_output(cmd, shell=True)
    ordered = spec_formatters._order_spec(spec.raw_spec)
    dirty_yaml = yaml.dump(ordered, sort_keys=False, width=4096).strip()
    cleaned_yaml = spec_formatters._clean_semi_formatted_yaml(dirty_yaml)
    try:
        if yaml.load(cleaned_yaml) != spec.raw_spec:
            print('yaml does not match raw')
            print(name)
            print(json.dumps(yaml.load(cleaned_yaml), indent=4))
            print(json.dumps(spec.raw_spec, indent=4))
    except Exception:
        print('yaml does not load')
        print(cleaned_yaml)
        print(dirty_yaml)

    example = {
        "json": json.dumps(ordered, cls=spec_formatters.MyEncoder, sort_keys=False, indent=2).strip(),
        "yaml": cleaned_yaml,
        "api": code.strip().replace('\n\n\n', '\n\n'),
        "command": cmd.strip(),
        "output": out.decode('utf-8').replace('\r', '').strip()
    }
    return example


"""
# Begin Processing

This needs to live outside of a function so that the result of the exec(code) will be in the available context
"""
os.environ['PYTHONIOENCODING'] = 'utf-8'
parser = argparse.ArgumentParser(description='')
parser.add_argument('-k', '--key-filter', dest='key_filter',
                    help='where to get the input')

args = parser.parse_args()

built_examples = {}
for name, iterations, fragment, pipes in EXAMPLES:
    if args.key_filter and name not in args.key_filter:
        continue
    code = template.replace('FRAGMENT', fragment)
    try:
        log.info(name)
        log.debug(code)
        exec(code)
        # spec should be created when running exec
        data = build_example(name, spec, iterations, pipes)
        built_examples[name] = data
    except (TypeError, SyntaxError) as err:
        print(err)
        print(name)
        print(code)
        raise Exception() from err
        # exit(-1)

print(json.dumps({"examples": built_examples}, cls=spec_formatters.MyEncoder, sort_keys=False, indent=2))
