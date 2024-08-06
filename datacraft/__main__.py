#!/bin/env python
"""
Entry point for datacraft tool
"""
import os.path
import sys

from . import cli, suppliers
from .logging_handler import *
# this activates the decorators, so they will be discoverable
from .preprocessor import *
from .supplier.exceptions import SupplierException

_log = logging.getLogger(__name__)


def wrap_main():
    """wraps main with try except for SpecException """
    try:
        main(sys.argv[1:])
    except (SpecException, SupplierException) as exc:
        _log.error(str(exc))


def main(argv):
    """Runs the tool """

    args = cli.parseargs(argv)
    cli.configure_logging(args)
    if args.server or args.endpoint_spec:
        run_server(args)
        return

    generator = cli.process_args(args)
    if generator is None:
        return

    _log.info('Starting Processing...')
    for _ in range(0, args.iterations):
        # Generator will handle writing to configured output
        next(generator)
    _log.info('Finished Processing')


def run_server(args):
    if args.endpoint_spec:
        if not os.path.exists(args.endpoint_spec):
            raise FileNotFoundError("No file at path %s", args.endpoint_spec)
        with open(args.endpoint_spec, "r", encoding="utf-8") as fp:
            endpoints_spec = json.load(fp)
        mappings = {endpoint: cli.generator_for_spec(args, spec) for endpoint, spec in endpoints_spec.items()}
    else:
        generator = cli.process_args(args)
        mappings = {args.endpoint: generator}

    try:
        from . import server
        using_template_or_formatter = args.template or args.format
        records_per_file = args.records_per_file
        if records_per_file is None:
            records_per_file = 1
        server.run(mappings,
                   args.port,
                   args.host,
                   data_is_json=(not using_template_or_formatter),
                   count_supplier=suppliers.count_supplier(count=records_per_file),
                   delay=args.server_delay)
    except ModuleNotFoundError:
        _log.warning('--server mode requires flask, pip/conda install flask and rerun command')


if __name__ == "__main__":
    main(sys.argv[1:])
