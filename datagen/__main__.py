#!/bin/env python
"""
Entry point for datagen tool
"""
import sys

# this activates the decorators, so they will be discoverable
from .preprocessor import *
from .schemas import *
from .logging_handler import *

log = logging.getLogger(__name__)


def wrap_main():
    """wraps main with try except for SpecException """
    try:
        main(sys.argv[1:])
    except SpecException as exc:
        log.error(str(exc))


def main(argv):
    """Runs the tool """

    args = datagen.cli.parseargs(argv)
    generator = datagen.cli.process_args(args)
    if generator is None:
        return
    if args.server:
        try:
            from . import server
            using_template_or_formatter = args.template or args.format
            server.run(generator, args.endpoint, data_is_json=(not using_template_or_formatter))
        except ModuleNotFoundError:
            log.warning('--server mode requires flask, pip/conda install flask and rerun command')
    else:
        log.info('Starting Processing...')
        for _ in range(0, args.iterations):
            # Generator will handle using to configured output
            next(generator)
        log.info('Finished Processing')
