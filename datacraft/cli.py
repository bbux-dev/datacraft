"""
Entry point for datacraft tool
"""
import argparse
import os
import sys
import json
import logging
from typing import Any

import yaml

from . import outputs, utils, usage
from . import template_engines, builder, spec_formatters, loader, registries, entrypoints
# this activates the decorators, so they will be discoverable
from .exceptions import SpecException

# need to import this to trigger registration process
from . import preprocessor, defaults, distributions, casters

_log = logging.getLogger(__name__)

_LOG_LEVELS = [
    "critical",
    "fatal",
    "error",
    "warning",
    "warn",
    "info",
    "debug",
    "off",
    "stop",
    "disable"
]
_LONG_DESCRIPTION = '''
Example Usage:

# create 10 records from the spec and print them out as a CSV with headers included
$ datacraft --spec spec.json --iterations 10 --format csv-with-headers --exclude-internal

# List field spec types registered
$ datacraft --type-list

# Get example spec and usage info for one or more listed types
$ datacraft --type-help values templated

# Inline YAML syntax, Generate 10 records as CSV and exclude internal fields
$ datacraft --inline '{id:uuid: {}, ts:date.iso: {}}' -i 10 --format csv -x

# Create 10 records with two records per file, and output these with a name of the form data-N.csv in the /tmp dir
$ datacraft --inline '{"id:cc-word?cnt=6": {}, "ts:date.iso.millis": {}}' \\
  -i 10 -r 2 \\
  --format csvh -x \\
  --prefix data \\
  --outfile-extension .csv \\
  -outdir /tmp

# Convert inline YAML spec to JSON format
$ datacraft --inline '{"id:cc-word?cnt=6": {}, "ts:date.iso?suffix='Z'": {}}' --debug-spec > /tmp/spec.json

# Convert existing JSON Spec to YAML
$ datacraft --spec /tmp/spec.json --debug-spec-yaml

# Turn on debug level logging
$ datacraft ... --log-level debug

# Turn off logging
$ datacraft ... --log-level off

See: https://datacraft.readthedocs.io/en/latest/ for detailed usage and documentation
'''


def parseargs(argv):
    """
    Parses the command line arguments

    Args:
        argv: the command line arguments

    Returns:
        args object
    """
    parser = argparse.ArgumentParser(description='Run datacraft.',
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog=_LONG_DESCRIPTION)
    group = parser.add_argument_group('input')
    group.add_argument('-s', '--spec', help='Spec to Use')
    group.add_argument('--inline', help='Spec as string')
    parser.add_argument('-i', '--iterations', default=100, type=int,
                        help='Number of Iterations to Execute')
    parser.add_argument('-o', '--outdir',
                        help='Output directory')
    parser.add_argument('-p', '--outfile-prefix', dest='outfile_prefix',
                        default=registries.get_default('outfile_prefix'),
                        help='Prefix for output files, default is generated')
    parser.add_argument('-ext', '--outfile-extension', dest='outfile_extension',
                        default=registries.get_default('outfile_extension'),
                        help='Extension to add to generated files, default is none')
    parser.add_argument('-t', '--template',
                        help='Path to template to populate, or template inline as a string')
    parser.add_argument('-r', '--records-per-file', dest='records_per_file', default=None, type=int,
                        help='Number of records to place in each file, default is all, requires -o to be specified')
    parser.add_argument('-k', '--printkey', action='store_true',
                        help='When printing to stdout field name should be printed along with value')
    parser.add_argument('-c', '--code', nargs='+',
                        help='Path to custom defined functions in one or more modules to load')
    parser.add_argument('-d', '--datadir',
                        help='Path to external directory to load external data files such as csvs')
    parser.add_argument('-l', '--log-level', dest='log_level', default="info", choices=_LOG_LEVELS,
                        help='Logging level verbosity, default is info')
    formats = str(registries.registered_formats())
    parser.add_argument('-f', '--format', default=None,
                        help='Formatter for output records, default is none, valid are: ' + formats)
    parser.add_argument('--strict', action='store_true',
                        default=registries.get_default('strict_mode'),
                        help='Enforce schema validation for all registered field specs')
    parser.add_argument('--apply-raw', action='store_true', dest='apply_raw',
                        help='Data from -s argument should be applied to the template with out treating as a Data Spec')
    debug_group = parser.add_argument_group('info')
    debug_group.add_argument('--debug-spec', dest='debug_spec', action='store_true',
                             help='Debug spec after internal reformatting')
    debug_group.add_argument('--debug-spec-yaml', dest='debug_spec_yaml', action='store_true',
                             help='Debug spec after internal reformatting, write out as yaml')
    debug_group.add_argument('--debug-defaults', dest='debug_defaults', action='store_true',
                             help='List default values from registry after any external code loading')
    debug_group.add_argument('--type-list', dest='type_list', action='store_true',
                             help='Write out the list of registered types')
    debug_group.add_argument('--type-help', dest='type_help', metavar='TYPE_NAME', default=argparse.SUPPRESS, nargs='*',
                             help='Write out the help for registered types, specify one or more types to limit help '
                                  'to, no arguments means show help for all types')
    debug_group.add_argument('--cast-list', dest='cast_list', action='store_true',
                             help='Write out the list of registered casters')
    debug_group.add_argument('--format-list', dest='format_list', action='store_true',
                             help='Write out the list of registered formatters')
    parser.add_argument('-x', '--exclude-internal', dest='exclude_internal', action='store_true',
                        default=registries.get_default('exclude_internal'),
                        help='Do not include non data fields in output records')
    parser.add_argument('--sample-lists', dest='sample_lists', action='store_true',
                        default=registries.get_default('sample_lists'),
                        help='Turns on sampling for all list backed types')
    parser.add_argument('--defaults', help='Path to defaults overrides')
    parser.add_argument("-sd", "--set-defaults", dest='set_defaults', metavar="KEY=VALUE", nargs='+',
                        help="Set a number of key-value pairs to override defaults with")
    parser.add_argument("--server", action='store_true',
                        help="Run a flask http server with the generated content")
    parser.add_argument("--server-endpoint", dest='endpoint', default='/data',
                        help="End point to host data service on")
    parser.add_argument("--suppress-output", dest='suppress_output', action='store_true',
                        help="Silent mode, no output other than logging produced, set --log-level off to turn off "
                             "logging")
    parser.add_argument("--var-file", dest='var_file',
                        help="JSON or YAML file with variables to apply to the spec before consuming")
    parser.add_argument("-v", "--vars", metavar="KEY=VALUE", nargs='+',
                        help="Set a number of key-value pairs variables to apply to the spec before consuming."
                             "These override those from --var-file")

    args = parser.parse_args(argv)

    return args


def process_args(args):
    """
    Processes the command line args and either writes out various artifacts such as config or interpolated specs,
    or creates the generator from the provided args.

    Args:
        args: from parsargs

    Returns:
        The constructed record generator or None
    """
    ###################
    # Set Up
    ###################

    _configure_logging(args)
    _log.info('Starting Loading Configurations...')
    _log.debug('Parsing Args')

    if args.code:
        _log.debug('Loading custom code from %s', args.code)
        for code in args.code:
            utils.load_custom_code(code)

    ###################
    # Default Overrides
    ###################
    _handle_defaults(args)

    # command line overrides any configs
    if args.sample_lists:
        registries.set_default('sample_mode', True)

    # print out the defaults as currently registered
    if args.debug_defaults:
        writer = outputs.get_writer(args.outdir, outfile='dataspec_defaults.json', overwrite=True)
        defaults_info = registries.all_defaults()
        writer.write(json.dumps(defaults_info, indent=4))
        return None

    # trigger any custom code loading
    entrypoints.load_eps()
    # this would bypass spec loading
    if args.type_list:
        all_types = registries.registered_types()
        return _write_info(info=all_types, dest_name='type_list.txt', outdir=args.outdir)
    if 'type_help' in args:
        usage_str = usage.build_cli_help(*args.type_help)
        return _write_info(info=usage_str, dest_name='type_help.txt', outdir=args.outdir)
    if args.cast_list:
        caster_names = casters.all_names()
        return _write_info(info=caster_names, dest_name='cast_list.txt', outdir=args.outdir)
    if args.format_list:
        all_formats = registries.registered_formats()
        return _write_info(info=all_formats, dest_name='format_list.txt', outdir=args.outdir)

    _log.debug('Attempting to load Data Spec from %s', args.spec if args.spec else args.inline)
    spec = _load_spec(args)
    if spec is None:
        return None

    ###################
    # By Pass Arguments
    ###################

    # Only dump out the reformatted spec
    if args.debug_spec:
        writer = _get_writer(args)
        raw_spec = loader.preprocess_spec(spec)
        writer.write(spec_formatters.format_json(raw_spec))
        return None
    if args.debug_spec_yaml:
        writer = _get_writer(args)
        raw_spec = loader.preprocess_spec(spec)
        writer.write(spec_formatters.format_yaml(raw_spec))
        return None

    # apply the spec as data to the template
    if args.apply_raw:
        engine = template_engines.for_file(args.template)
        writer = _get_writer(args)
        writer.write(engine.process(spec))
        return None

    ###################
    # Regular Flow
    ##################
    processor = outputs.processor(args.template, args.format)
    writer = _get_writer(args)
    output = _get_output(args, processor, writer)

    generator = builder.generator(
        spec,
        args.iterations,
        enforce_schema=args.strict,
        data_dir=args.datadir,
        exclude_internal=args.exclude_internal,
        output=output,
        processor=processor)

    return generator


def _write_info(info: Any, dest_name: str, outdir: Any) -> None:
    """Writes debug info to stdout or disk"""
    writer = outputs.get_writer(outdir, outfile=dest_name, overwrite=True)
    if isinstance(info, str):
        info_str = info
    else:
        info_str = '\n'.join(info)
    writer.write(info_str)


def _handle_defaults(args):
    """ process and populate new/overridden defaults """
    if args.defaults:
        defaults_info = _load_json_or_yaml(args.defaults, {})
        for key, value in defaults_info.items():
            registries.set_default(key, value)
    # command line takes precedence over config file
    if args.set_defaults:
        for setting in args.set_defaults:
            parts = setting.split('=')
            if len(parts) != 2:
                _log.warning('Invalid default override: should be of form key=value or key="value with spaces": %s',
                             setting)
                continue
            registries.set_default(parts[0].strip(), parts[1])


def _get_writer(args):
    """ get the write from the args """
    return outputs.get_writer(args.outdir,
                              outfile_prefix=args.outfile_prefix,
                              extension=args.outfile_extension,
                              server=args.server,
                              suppress_output=(args.suppress_output or args.server))


def _get_output(args, processor, writer):
    """ get the output from the args, processor, and writer """
    if processor:
        records_per_file = args.records_per_file
        if records_per_file is None:
            records_per_file = sys.maxsize
        return outputs.record_level(processor, writer, records_per_file)

    return outputs.single_field(writer, args.printkey)


def _load_spec(args):
    """
    Attempts to load the spec first as JSON then as YAML if JSON fails.
    Returns
        Data Spec as Dictionary if loaded correctly.
    """
    spec_path = args.spec
    inline = args.inline
    if spec_path is None and inline is None:
        raise SpecException('One of --spec <spec path> or --inline "<spec string>" must be specified')
    if spec_path and inline:
        raise SpecException('Only one of --spec <spec path> or --inline "<spec string>" must be specified')

    # template replacements for specs, if provided
    template_vars = _load_template_vars(args)
    if template_vars is None:
        # something went wrong, should at least be empty, logs will indicate what
        return None

    if inline:
        return _parse_spec_string(inline, template_vars)
    return _load_json_or_yaml(spec_path, template_vars)


def _load_template_vars(args):
    template_vars = {}
    if args.var_file:
        if not os.path.exists(args.var_file):
            _log.error('Unable to load var file from path: %s', args.var_file)
            return None
        template_vars = _load_json_or_yaml(args.var_file, {})
    if args.vars:
        for item in args.vars:
            parts = item.split('=')
            if len(parts) != 2:
                _log.warning('Invalid template var: should be of form key=value or key="value with spaces": %s', item)
                continue
            template_vars[parts[0].strip()] = parts[1]
    return template_vars


def _load_json_or_yaml(data_path, template_vars):
    """ attempts to load the data at path as JSON, if that fails tries as YAML """
    if not os.path.exists(data_path):
        _log.error('Unable to load data from path: %s', data_path)
        return None

    if len(template_vars) > 0:
        _log.debug('Applying %s template vars to raw spec', len(template_vars))
        spec_str = template_engines.for_file(data_path).process(template_vars)
        _log.debug('Attempting to load data as JSON')
    else:
        spec_str = utils.load_file_as_string(data_path)
    try:
        return json.loads(spec_str)
    except json.decoder.JSONDecodeError:
        _log.debug('Data is not Valid JSON')
    # not JSON, try yaml
    _log.debug('Attempting to load data as YAML')
    try:
        loaded = yaml.safe_load(spec_str)
    except yaml.parser.ParserError as err:
        _log.warning(err)
        loaded = None
    if not isinstance(loaded, dict):
        raise SpecException(f'Unable to load data from path: {data_path}, Please verify it is valid JSON or YAML')
    return loaded


def _parse_spec_string(inline: str, template_vars: dict) -> dict:
    """
    Attempts to parse the string into a datacraft DataSpec. First tries to interpret as JSON, then as YAML.

    Returns:
        the parsed spec as a Dictionary
    """
    if len(template_vars) > 0:
        inline = template_engines.string(inline).process(template_vars)
    if inline is None or inline.strip() == "":
        raise SpecException(f'Unable to load spec from empty string: {inline}, Please verify it is valid JSON or YAML')
    try:
        return json.loads(inline)
    except json.decoder.JSONDecodeError as err:
        _log.debug('Spec is not Valid JSON: %s', str(err))

    # not JSON, try yaml
    _log.debug('Attempting to load spec as YAML')
    try:
        return yaml.load(inline, Loader=yaml.FullLoader)
    except yaml.parser.ParserError as err:
        _log.debug('Spec is not Valid YAML %s', str(err))
    raise SpecException(f'Unable to load spec from string: {inline}, Please verify it is valid JSON or YAML')


def _configure_logging(args):
    """
    Use each logging element from the registry to configure logging
    """
    for name in registries.Registry.logging.get_all():
        configure_function = registries.Registry.logging.get(name)
        configure_function(args.log_level)
