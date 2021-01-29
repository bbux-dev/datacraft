"""
Default module for configuring logging
"""
import logging
import dataspec


@dataspec.registry.logging('default')
def configure_logging(loglevel):
    """
    Default Handler for Logging Configuration
    :param loglevel: loglevel as specified from the command line
    :return: None
    """
    mapping = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warn": logging.WARN,
        "error": logging.ERROR
    }
    level = mapping.get(loglevel, logging.INFO)
    logging.basicConfig(
        format='%(levelname)s [%(asctime)s] %(message)s',
        level=level,
        datefmt='%d-%b-%Y %I:%M:%S %p'
    )
