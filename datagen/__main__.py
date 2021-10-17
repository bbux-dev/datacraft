#!/bin/env python
"""
Entry point for datagen tool
"""
import os
import sys
import json
import argparse
import logging
import yaml

from . import outputs, utils, types, preprocessor, template_engines, builder, SpecException
# this activates the decorators, so they will be discoverable
from .supplier import *
from .defaults import *
from .preprocessor import *
from .logging_handler import *

log = logging.getLogger(__name__)


def wrap_main():
    """ wraps main with try except for SpecException """
    try:
        main(sys.argv[1:])
    except SpecException as exc:
        log.error(str(exc))


def main(argv):
    """
    Runs the tool
    """
    parser = argparse.ArgumentParser(description='Run datagen.')
    group = parser.add_argument_group('input')
    group.add_argument('-s', '--spec', help='Spec to Use')
    group.add_argument('--inline', help='Spec as string')
    parser.add_argument('-i', '--iterations', default=100, type=int,
                        help='Number of Iterations to Execute')
    parser.add_argument('-o', '--outdir',
                        help='Output directory')
    parser.add_argument('-p', '--outfile-prefix', dest='outfileprefix', default='generated',
                        help='Prefix for output files, default is generated')
    parser.add_argument('-e', '--extension', default='',
                        help='Extension to add to generated files')
    parser.add_argument('-t', '--template',
                        help='Path to template to populate, or template inline as a string')
    parser.add_argument('-r', '--records-per-file', dest='recordsperfile', default=sys.maxsize, type=int,
                        help='Number of records to place in each file, default is all, requires -o to be specified')
    parser.add_argument('-k', '--printkey', action='store_true', default=False,
                        help='When printing to stdout field name should be printed along with value')
    parser.add_argument('-c', '--code', nargs='+',
                        help='Path to custom defined functions in one or more modules to load')
    parser.add_argument('-d', '--datadir',
                        help='Path to external directory to load external data files such as csvs')
    parser.add_argument('-l', '--log-level', dest='log_level', default=logging.INFO,
                        help='Logging level verbosity, default is info, valid are "debug","info","warn","error","off"')
    formats = str(types.valid_formats())
    parser.add_argument('-f', '--format', default=None,
                        help='Formatter for output records, default is none, valid are: ' + formats)
    parser.add_argument('--strict', action='store_true', default=False,
                        help='Enforce schema validation for all registered field specs')
    parser.add_argument('--apply-raw', action='store_true', dest='apply_raw', default=False,
                        help='Data from -s argument should be applied to the template with out treating as a Data Spec')
    parser.add_argument('--debug-spec', dest='debug_spec', action='store_true', default=False,
                        help='Debug spec after internal reformatting')
    parser.add_argument('--debug-defaults', dest='debug_defaults', action='store_true', default=False,
                        help='List default values from registry after any external code loading')
    parser.add_argument('-x', '--exclude-internal', dest='exclude_internal', action='store_true', default=False,
                        help='Do not include non data fields in output records')
    parser.add_argument('--sample-lists', dest='sample_lists', action='store_true', default=False,
                        help='Turns on sampling for all list backed types')
    parser.add_argument('--defaults', help='Path to defaults overrides')
    parser.add_argument("--set-defaults", dest='set_defaults', metavar="KEY=VALUE", nargs='+',
                        help="Set a number of key-value pairs to override defaults with")

    args = parser.parse_args(argv)

    ###################
    # Set Up
    ###################

    _configure_logging(args)
    log.info('Starting Loading Configurations...')
    log.debug('Parsing Args')

    if args.code:
        log.debug('Loading custom code from %s', args.code)
        for code in args.code:
            utils.load_custom_code(code)

    ###################
    # Default Overrides
    ###################
    if args.defaults:
        defaults = _load_json_or_yaml(args.defaults)
        for key, value in defaults.items():
            types.set_default(key, value)
    # command line takes precedence over config file
    if args.set_defaults:
        for setting in args.set_defaults:
            parts = setting.split('=')
            if len(parts) != 2:
                log.warning('Invalid default override: should be of form key=value or key="value with spaces": %s',
                            setting)
                continue
            types.set_default(parts[0], parts[1])
    # command line overrides any configs
    if args.sample_lists:
        types.set_default('sample_mode', True)

    # print out the defaults as currently registered
    if args.debug_defaults:
        writer = _get_writer(args, outfile='dataspec_defaults.json', overwrite=True)
        defaults = types.all_defaults()
        writer.write(json.dumps(defaults, indent=4))
        return

    ###################
    # Load Data Spec
    ###################

    log.debug('Attempting to load Data Spec from %s', args.spec if args.spec else args.inline)
    spec = _load_spec(args)
    if spec is None:
        return

    ###################
    # By Pass Arguments
    ###################

    # Only dump out the reformatted spec
    if args.debug_spec:
        writer = _get_writer(args)
        writer.write(json.dumps(preprocessor.preprocess_spec(spec), indent=4))
        return

    # apply the spec as data to the template
    if args.apply_raw:
        engine = template_engines.for_file(args.template)
        writer = _get_writer(args)
        writer.write(engine.process(spec))
        return

    ###################
    # Regular Flow
    ##################
    output = _configure_output(args)

    log.info('Starting Processing...')
    generator = builder.generator(
        spec,
        args.iterations,
        enforce_schema=args.strict,
        data_dir=args.datadir,
        exclude_internal=args.exclude_internal,
        output=output)
    for _ in range(0, args.iterations):
        # Generator will handle using to configured output
        next(generator)
    log.info('Finished Processing')



def _configure_output(args):
    """
    Configures the output. Loads templates and applies the specified formatter if any.
    If none of these configurations are specified, it will return the default output
    which is to print each value to standard out.
    """
    writer = _get_writer(args)

    if args.template:
        log.debug('Using template: %s', args.template)
        if '{{' in args.template:
            engine = template_engines.string(args.template)
        else:
            engine = template_engines.for_file(args.template)
        return outputs.RecordLevelOutput(engine, writer)

    if args.format:
        log.debug('Using %s formatter for output', args.format)
        formatter = outputs.FormatProcessor(args.format)
        return outputs.RecordLevelOutput(formatter, writer)

    # default
    return outputs.SingleFieldOutput(writer, args.printkey)


def _get_writer(args, outfile: str = None, overwrite: bool = False) -> outputs.WriterInterface:
    """
    creates the appropriate output writer from the given args and params

    If no output directory is specified/configured will write to stdout
    """
    if args.outdir:
        log.debug('Creating output file writer for dir: %s', args.outdir)
        if outfile:
            writer = outputs.single_file_writer(
                outdir=args.outdir,
                outname=outfile,
                overwrite=overwrite
            )
        else:
            writer = outputs.incrementing_file_writer(
                outdir=args.outdir,
                outname=args.outfileprefix,
                extension=args.extension,
                records_per_file=args.recordsperfile
            )
    else:
        log.debug('Writing output to stdout')
        writer = outputs.StdOutWriter()
    return writer


def _load_spec(args):
    """
    Attempts to load the spec first as JSON then as YAML if JSON fails.
    :returns: Data Spec as Dictionary if loaded correctly.
    """
    spec_path = args.spec
    inline = args.inline
    if spec_path is None and inline is None:
        raise SpecException('One of --spec <spec path> or --inline "<spec string>" must be specified')
    if spec_path and inline:
        raise SpecException('Only one of --spec <spec path> or --inline "<spec string>" must be specified')
    if inline:
        return _parse_spec_string(inline)
    return _load_json_or_yaml(data_path=spec_path)


def _load_json_or_yaml(data_path):
    """ attempts to load the data at path as JSON, if that fails tries as YAML """
    if not os.path.exists(data_path):
        log.error('Unable to load data from path: %s', data_path)
        return None
    with open(data_path, 'r') as handle:
        log.debug('Attempting to load data as JSON')
        try:
            return json.load(handle)
        except json.decoder.JSONDecodeError:
            log.debug('Data is not Valid JSON')
    # not JSON, try yaml
    with open(data_path, 'r') as handle:
        log.debug('Attempting to load data as YAML')
        loaded = yaml.load(handle, Loader=yaml.FullLoader)
    if not isinstance(loaded, dict):
        raise SpecException(f'Unable to load data from path: {data_path}, Please verify it is valid JSON or YAML')
    return loaded


def _parse_spec_string(inline: str):
    """
    Attempts to parse the string into a datagen DataSpec. First tries to interpret as JSON, then as YAML.
    :return: the parsed spec as a Dictionary
    """

    try:
        return json.loads(inline)
    except json.decoder.JSONDecodeError:
        log.debug('Spec is not Valid JSON')
    # not JSON, try yaml
    log.debug('Attempting to load spec as YAML')
    spec = yaml.load(inline, Loader=yaml.FullLoader)
    if not isinstance(spec, dict):
        raise SpecException(f'Unable to load spec from string: {inline}, Please verify it is valid JSON or YAML')
    return spec


def _configure_logging(args):
    """
    Use each logging element from the registry to configure logging
    """
    for name in types.registry.logging.get_all():
        configure_function = types.registry.logging.get(name)
        configure_function(args.log_level)

