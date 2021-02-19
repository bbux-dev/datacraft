#!/bin/env python
import json
import argparse
from jinja2 import Environment, FileSystemLoader, select_autoescape

def main():
    parser = argparse.ArgumentParser(description='')

    parser.add_argument('-i', '--input', default="",
                        required=True, help='where to get the input')
    parser.add_argument('-t', '--template', default="FIELDSPECS.jinja.md",
                        help='where to get the input')
    parser.add_argument('-m', '--mode', default="verify", choices=['verify', 'test', 'apply', 'all'],
                        help='what mode to run in')

    args = parser.parse_args()

    with open(args.input) as f:
        data = json.load(f)

    if args.mode == 'verify' or args.mode == 'all':
        verify_data(data)
    if args.mode == 'apply' or args.mode == 'all':
        apply_template(data, args.template)


def verify_data(data):
    any_errors = False
    for key, value in data.items():
        if not key.startswith('json_spec'):
            # skip yaml for now
            continue
        # try to load as json
        try:
            json.loads(value)
        except json.decoder.JSONDecodeError as err:
            any_errors = True
            print(f'{key}: error: {str(err)}')
            print(value)
    if any_errors:
        raise Exception('Not all specs parsed successfully!')


def apply_template(data, template_name):
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template(template_name)
    print(template.render(data))

if __name__ == '__main__':
    main()
