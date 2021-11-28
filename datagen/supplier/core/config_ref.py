"""
Module for config_ref type

"""
import datagen


@datagen.registry.types('config_ref')
def _configure_handler(_, __):
    """" Does nothing, just place holder """
