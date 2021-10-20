"""
Default module for configuring logging
"""
import logging
import datagen

_MAPPING = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warn": logging.WARN,
    "error": logging.ERROR
}


@datagen.registry.logging('default')
def configure_logging(loglevel: str):
    """Default Handler for Logging Configuration

    Args:
        loglevel: loglevel as specified from the command line
    """
    if str(loglevel).lower() in ['off', 'stop', 'disable']:
        logging.disable(logging.CRITICAL)
    else:
        level = _MAPPING.get(loglevel, logging.INFO)
        logging.basicConfig(
            format='%(levelname)s [%(asctime)s] %(message)s',
            level=level,
            datefmt='%d-%b-%Y %I:%M:%S %p'
        )