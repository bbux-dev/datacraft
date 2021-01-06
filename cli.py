#!/bin/env python3
import json
import argparse
from datamaker import Loader
from datamaker import StdOutOutputer
import datamaker.types as types


def main():
    parser = argparse.ArgumentParser(description='Run datamaker.')
    parser.add_argument('-s', '--spec', required=True,
                        help='Spec to Use')
    parser.add_argument('-i', '--iterations', default=100, type=int,
                        help='Number of Iterations to Execute')

    args = parser.parse_args()

    with open(args.spec, 'r') as handle:
        spec = json.load(handle)

    registry = types.defaults()
    loader = Loader(spec, registry)
    output = StdOutOutputer()
    keys = [key for key in spec.keys() if key != 'refs']

    for i in range(0, args.iterations):
        for key in keys:
            value = loader.get(key).next(i)
            output.handle(key, value)


if __name__ == '__main__':
    main()
