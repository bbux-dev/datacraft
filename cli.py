#!/bin/env python3
import json
import argparse
from datamaker import Loader
import datamaker.types as types
import datamaker.template_engines as engines
import datamaker.outputs as outputs


def main():
    parser = argparse.ArgumentParser(description='Run datamaker.')
    parser.add_argument('-s', '--spec', required=True,
                        help='Spec to Use')
    parser.add_argument('-i', '--iterations', default=100, type=int,
                        help='Number of Iterations to Execute')
    parser.add_argument('-o', '--outdir',
                        help='Output directory')
    parser.add_argument('-p', '--outfileprefix', default='generated',
                        help='Prefix fore output files, default is generated')
    parser.add_argument('-e', '--extension', default='',
                        help='Extension to add to generated files')
    parser.add_argument('-t', '--template',
                        help='Path to template to populate')
    parser.add_argument('-r', '--recordsperfile', default=1, type=int,
                        help='Number of records to place in each file, default is 1, requires -o to be specified')
    parser.add_argument('-k', '--printkey', default=False,
                        help='When printing to stdout field name should be printed along with value')

    args = parser.parse_args()

    with open(args.spec, 'r') as handle:
        spec = json.load(handle)

    registry = types.defaults()
    loader = Loader(spec, registry)

    if args.outdir:
        writer = outputs.FileWriter(
            outdir=args.outdir,
            outname=args.outfileprefix,
            extension=args.extension,
            records_per_file=args.recordsperfile

        )
    else:
        writer = outputs.StdOutWriter()

    if args.template:
        output = outputs.RecordLevelOutput(engines.load(args.template), writer)
    else:
        output = outputs.SingleFieldOutput(writer, args.printkey)

    keys = [key for key in spec.keys() if key != 'refs']

    for i in range(0, args.iterations):
        for key in keys:
            value = loader.get(key).next(i)
            output.handle(key, value)
        output.finished_record()


if __name__ == '__main__':
    main()
