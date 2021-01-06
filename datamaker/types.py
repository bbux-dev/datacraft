from .type_handlers import combine
from .type_handlers import weighted_ref


class TypeRegistry(object):
    def __init__(self):
        self._internal = {}

    def register(self, key, handler):
        self._internal[key] = handler

    def lookup(self, key):
        return self._internal.get(key)


def defaults():
    """
    Creates the default builtin type handlers
    :return: the default registry
    """
    registry = TypeRegistry()
    registry.register('combine', combine)
    registry.register('weightedref', weighted_ref)
    return registry
