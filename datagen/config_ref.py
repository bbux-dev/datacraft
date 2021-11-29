"""
Module for config_ref type

"""
from . import types


@types.registry.types('config_ref')
def _configure_handler(_, __):
    """" Does nothing, just place holder """
