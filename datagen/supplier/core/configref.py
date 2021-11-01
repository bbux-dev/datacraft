"""
Module for configref types
"""
import datagen


@datagen.registry.types('configref')
def _configure_handler(_, __):
    """" Does nothing, just place holder """
