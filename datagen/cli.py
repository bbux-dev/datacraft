"""
Entry point for datagen tool
"""
import argparse
import os
import sys

import yaml

# this activates the decorators, so they will be discoverable
from . import outputs
from . import utils, types, template_engines, builder, spec_formatters, loader
from .preprocessor import *
from .schemas import *

log = logging.getLogger(__name__)


def parseargs(argv):
    """
    Parses the command line arguments

    Args:
        argv: the command line arguments

    Returns:
        args object
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
    parser.add_argument('--debug-spec-yaml', dest='debug_spec_yaml', action='store_true', default=False,
                        help='Debug spec after internal reformatting, write out as yaml')
    parser.add_argument('--debug-defaults', dest='debug_defaults', action='store_true', default=False,
                        help='List default values from registry after any external code loading')
    parser.add_argument('-x', '--exclude-internal', dest='exclude_internal', action='store_true', default=False,
                        help='Do not include non data fields in output records')
    parser.add_argument('--sample-lists', dest='sample_lists', action='store_true', default=False,
                        help='Turns on sampling for all list backed types')
    parser.add_argument('--defaults', help='Path to defaults overrides')
    parser.add_argument("--set-defaults", dest='set_defaults', metavar="KEY=VALUE", nargs='+',
                        help="Set a number of key-value pairs to override defaults with")
    parser.add_argument("--server", action='store_true',
                        help="Run a flask http server with the generated content")
    parser.add_argument("--server-endpoint", dest='endpoint', default='/data',
                        help="End point to host data service on")
    parser.add_argument("--suppress-output", dest='suppress_output', action='store_true',
                        help="Silent mode, no output other than logging produced, set --log-level off to turn off "
                             "logging")

    args = parser.parse_args(argv)

    return args


def process_args(args):
    """
    Processes the command line args and either writes out various artifacts such as config or interpolated specs,
    or creates the generator from the provided args.

    Args:
        args: from cli.parsargs

    Returns:
        The constructed record generator or None
    """
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
        writer = outputs.get_writer(args.outdir, outfile='dataspec_defaults.json', overwrite=True)
        defaults = types.all_defaults()
        writer.write(json.dumps(defaults, indent=4))
        return None

    ###################
    # Load Data Spec
    ###################

    log.debug('Attempting to load Data Spec from %s', args.spec if args.spec else args.inline)
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
    output = outputs.configure_output(writer, processor, args.printkey)

    generator = builder.generator(
        spec,
        args.iterations,
        enforce_schema=args.strict,
        data_dir=args.datadir,
        exclude_internal=args.exclude_internal,
        output=output,
        processor=processor)

    return generator


def _get_writer(args):
    return outputs.get_writer(args.outdir,
                              outfileprefix=args.outfileprefix,
                              extension=args.extension,
                              recordsperfile=args.recordsperfile,
                              server=args.server,
                              suppress_output=(args.suppress_output or args.server))

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
        try:
            loaded = yaml.load(handle, Loader=yaml.FullLoader)
        except yaml.parser.ParserError as err:
            log.warning(err)
            loaded = None
    if not isinstance(loaded, dict):
        raise SpecException(f'Unable to load data from path: {data_path}, Please verify it is valid JSON or YAML')
    return loaded


def _parse_spec_string(inline: str):
    """
    Attempts to parse the string into a datagen DataSpec. First tries to interpret as JSON, then as YAML.

    Returns:
        the parsed spec as a Dictionary
    """
    if inline is None or inline.strip() == "":
        raise SpecException(f'Unable to load spec from empty string: {inline}, Please verify it is valid JSON or YAML')
    try:
        return json.loads(inline)
    except json.decoder.JSONDecodeError as err:
        log.debug('Spec is not Valid JSON: %s', str(err))
    # not JSON, try yaml
    log.debug('Attempting to load spec as YAML')
    try:
        return yaml.load(inline, Loader=yaml.FullLoader)
    except yaml.parser.ParserError as err:
        log.debug('Spec is not Valid YAML %s', str(err))
    raise SpecException(f'Unable to load spec from string: {inline}, Please verify it is valid JSON or YAML')


def _configure_logging(args):
    """
    Use each logging element from the registry to configure logging
    """
    for name in types.registry.logging.get_all():
        configure_function = types.registry.logging.get(name)
        configure_function(args.log_level)
