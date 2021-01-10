import json
import argparse
from datamaker import Loader
import datamaker.template_engines as engines
import datamaker.outputs as outputs
from datamaker import utils
# this activates the decorators, so they will be discoverable
# cannot use * import due to pyinstaller not recognizing modules as being used
from datamaker.type_handlers import combine
from datamaker.type_handlers import range_handler
from datamaker.type_handlers import select_list_subset
from datamaker.type_handlers import weighted_ref

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
    parser.add_argument('-c', '--code', nargs='+',
                        help='Path to custom defined functions in one or more modules to load')

    args = parser.parse_args()

    if args.code:
        for code in args.code:
            utils.load_custom_code(code)

    with open(args.spec, 'r') as handle:
        spec = json.load(handle)

    loader = Loader(spec)

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
