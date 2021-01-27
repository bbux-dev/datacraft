import json
import yaml
import argparse
from dataspec import Loader
import dataspec.template_engines as engines
import dataspec.outputs as outputs
from dataspec import utils
from dataspec import SpecException
# this activates the decorators, so they will be discoverable
# cannot use * import due to pyinstaller not recognizing modules as being used
from dataspec.type_handlers import combine
from dataspec.type_handlers import range_handler
from dataspec.type_handlers import select_list_subset
from dataspec.type_handlers import weighted_ref
from dataspec.type_handlers import uuid_handler
from dataspec.type_handlers import ip_handler
from dataspec.type_handlers import date_handler

def main():
    parser = argparse.ArgumentParser(description='Run dataspec.')
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

    spec = _load_spec(args.spec)

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

    keys = [key for key in loader.specs.keys() if key != 'refs']

    for i in range(0, args.iterations):
        for key in keys:
            value = loader.get(key).next(i)
            output.handle(key, value)
        output.finished_record()


def _load_spec(spec_path):
    with open(spec_path, 'r') as handle:
        try:
            return json.load(handle)
        except json.decoder.JSONDecodeError:
            pass
    # not JSON, try yaml
    with open(spec_path, 'r') as handle:
        spec = yaml.load(handle, Loader=yaml.FullLoader)
    if not isinstance(spec, dict):
        raise SpecException(f'Unable to load spec from path: {spec_path}, Please verify it is valid JSON or YAML')


if __name__ == '__main__':
    main()
