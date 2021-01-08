from .type_handlers import combine
from .type_handlers import weighted_ref
from .type_handlers import select_list_subset
from .type_handlers import range_handler


class TypeRegistry:
    """
    Holds the handlers that are registered for the environment.

    The signature for a handler is:

    def configure_supplier(data_spec, loader):
        ...
        return configured_supplier

    The signature for a supplier is:

    def next(self, iteration):
        ...
        return next_data

    A Field Spec will be routed to the handler based on the type key:

    {
      "field name": {
        "type": "reverse_string",
        "ref": "FORWARD_STRINGS"
      }
    }
    """
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
    registry.register('select_list_subset', select_list_subset)
    registry.register('range', range_handler)
    return registry
