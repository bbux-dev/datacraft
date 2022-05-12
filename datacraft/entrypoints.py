"""module for managing entry point loading"""
import logging
import importlib_metadata as metadata

_log = logging.getLogger(__name__)


class _EpsLoadedMark:
    """class to make sure entry points are only loaded once"""
    def __init__(self):
        self.mark = False

    def set(self, val: bool):
        self.mark = val


_eps_loaded = _EpsLoadedMark()


def load_eps():
    """initiate any custom entry points"""
    if _eps_loaded.mark:
        _log.debug('Mark Already Set')
        return
    eps = metadata.entry_points().get('datacraft.custom_type_loader', [])

    for ep in eps:
        plugin = ep.load()
        _log.info('Loading custom type loader: %s', ep.name)
        try:
            plugin()
        except Exception as err:
            _log.warning('Unable to initiate plugin: %s, error: %s', str(plugin), str(err))

    _eps_loaded.set(True)
