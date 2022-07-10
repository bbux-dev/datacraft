"""
Default module for configuring logging
"""
import logging

from . import registries


@registries.Registry.logging('default')
def _configure_logging(loglevel: str):
    """
    Default Handler for Logging Configuration

    Args:
        loglevel: loglevel as specified from the command line
    """
    if str(loglevel).lower() in ['off', 'stop', 'disable']:
        logging.disable(logging.CRITICAL)
    else:
        numeric_level = getattr(logging, loglevel.upper(), None)
        if not isinstance(numeric_level, int):
            raise ValueError(f'Invalid log level: {loglevel}')
        logging.basicConfig(
            format='%(levelname)s [%(asctime)s] %(message)s',
            level=numeric_level,
            datefmt='%d-%b-%Y %I:%M:%S %p'
        )
