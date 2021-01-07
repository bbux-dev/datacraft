#!/bin/env python3
import json
import argparse
from datamaker import Loader
from datamaker import StdOutOutputer
from datamaker import TemplateOutput
import datamaker.types as types
import datamaker.template_engines as engines


def main():
    parser = argparse.ArgumentParser(description='Run datamaker.')
    parser.add_argument('-s', '--spec', required=True,
                        help='Spec to Use')
    parser.add_argument('-i', '--iterations', default=100, type=int,
                        help='Number of Iterations to Execute')
    parser.add_argument('-t', '--template',
                        help='Path to template to populate')

    args = parser.parse_args()

    with open(args.spec, 'r') as handle:
        spec = json.load(handle)

    registry = types.defaults()
    loader = Loader(spec, registry)
    if args.template:
        output = TemplateOutput(engines.load(args.template))
    else:
        output = StdOutOutputer()
    keys = [key for key in spec.keys() if key != 'refs']

    for i in range(0, args.iterations):
        for key in keys:
            value = loader.get(key).next(i)
            output.handle(key, value)
        output.finished_record()


if __name__ == '__main__':
    main()
