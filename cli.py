#!/bin/env python

import json
import yaml
import argparse
import logging
from dataspec import Loader
import dataspec.template_engines as engines
import dataspec.outputs as outputs
from dataspec import utils
from dataspec import SpecException

log = logging.getLogger(__name__)


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
    parser.add_argument('-d', '--datadir',
                        help='Path to external directory to load external data file such as csvs')
    parser.add_argument('-l', '--loglevel', default=logging.INFO,
                        help='Logging level verbosity, default is info, valid are "debug","info","warn","error"')

    try:
        args = parser.parse_args()

        _configure_logging(args)
        log.info('Starting Loading Configurations...')
        log.debug("Parsing Args")

        if args.code:
            log.debug(f'Loading custom code from {args.code}')
            for code in args.code:
                utils.load_custom_code(code)

        log.debug(f'Attempting to load Data Spec from {args.spec}')
        spec = _load_spec(args.spec)
        loader = Loader(spec, args.datadir)

        if args.outdir:
            log.debug(f'Creating output file writer for dir: {args.outdir}')
            writer = outputs.FileWriter(
                outdir=args.outdir,
                outname=args.outfileprefix,
                extension=args.extension,
                records_per_file=args.recordsperfile
            )
        else:
            log.debug(f'Writing output to stdout')
            writer = outputs.StdOutWriter()

        if args.template:
            log.debug(f'Using template from specified file: {args.template}')
            output = outputs.RecordLevelOutput(engines.load(args.template), writer)
        else:
            output = outputs.SingleFieldOutput(writer, args.printkey)

        keys = [key for key in loader.specs.keys() if key != 'refs']

        log.info('Starting Processing...')
        for i in range(0, args.iterations):
            for key in keys:
                value = loader.get(key).next(i)
                output.handle(key, value)
            output.finished_record()
        log.info('Finished Processing')
    except SpecException as e:
        log.error(str(e))


def _load_spec(spec_path):
    with open(spec_path, 'r') as handle:
        log.debug('Attempting to load spec as JSON')
        try:
            return json.load(handle)
        except json.decoder.JSONDecodeError:
            log.debug('Spec is not Valid JSON')
            pass
    # not JSON, try yaml
    with open(spec_path, 'r') as handle:
        log.debug('Attempting to load spec as YAML')
        spec = yaml.load(handle, Loader=yaml.FullLoader)
    if not isinstance(spec, dict):
        raise SpecException(f'Unable to load spec from path: {spec_path}, Please verify it is valid JSON or YAML')
    return spec


def _configure_logging(args):
    for name in dataspec.registry.logging.get_all():
        configure_function = dataspec.registry.logging.get(name)
        configure_function(args.loglevel)


if __name__ == '__main__':
    # this activates the decorators, so they will be discoverable
    # cannot use * import due to pyinstaller not recognizing modules as being used
    from dataspec.type_handlers import combine
    from dataspec.type_handlers import range_handler
    from dataspec.type_handlers import select_list_subset
    from dataspec.type_handlers import weighted_ref
    from dataspec.type_handlers import uuid_handler
    from dataspec.type_handlers import ip_handler
    from dataspec.type_handlers import date_handler
    from dataspec.type_handlers import csv_handler
    import dataspec.logging

    main()
