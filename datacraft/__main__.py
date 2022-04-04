#!/bin/env python
"""
Entry point for datacraft tool
"""
import sys

from . import cli, suppliers
from .supplier.exceptions import SupplierException
# this activates the decorators, so they will be discoverable
from .preprocessor import *
from .logging_handler import *


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
    generator = cli.process_args(args)
    if generator is None:
        return
    if args.server:
        try:
            from . import server
            using_template_or_formatter = args.template or args.format
            records_per_file = args.records_per_file
            if records_per_file is None:
                records_per_file = 1
            server.run(generator,
                       args.endpoint,
                       data_is_json=(not using_template_or_formatter),
                       count_supplier=suppliers.count_supplier(count=records_per_file))
        except ModuleNotFoundError:
            _log.warning('--server mode requires flask, pip/conda install flask and rerun command')
    else:
        _log.info('Starting Processing...')
        for _ in range(0, args.iterations):
            # Generator will handle using to configured output
            next(generator)
        _log.info('Finished Processing')
