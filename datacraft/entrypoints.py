"""module for managing entry point loading"""
from functools import lru_cache
import logging
import importlib_metadata as metadata

import datacraft._registered_types.schemas

_log = logging.getLogger(__name__)


@lru_cache()
def load_eps():
    """initiate any custom entry points"""
    eps = metadata.entry_points().get('datacraft.custom_type_loader', [])

    for ep in eps:
        plugin = ep.load()
        _log.info('Loading custom type loader: %s', ep.name)
        try:
            plugin()
        except Exception as err:
            _log.warning('Unable to initiate plugin: %s, error: %s', str(plugin), str(err))

    return True
