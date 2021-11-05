"""
Module for the datagen registration system
"""
import logging
from typing import Any

import catalogue  # type: ignore

log = logging.getLogger(__name__)


class registry:
    """
    Catalogue registry for types, preprocessors, logging configuration, and others

    Attributes:
        types (catalogue.Registry): types for field specs
        schemas (catalogue.Registry): schemas for field spec types
        preprocessors (catalogue.Registry): functions to modify specs before running
        logging (catalogue.Registry): custom logging setup
        formats (catalogue.Registry): registered formats for output
        distribution (catalogue.Registry): different numeric distributions, normal, uniform, etc
        defaults (catalogue.Registry): default values

    Examples:
        >>> import datagen
        >>> @datagen.registry.types('special')
        ... def _handle_special_type(field_spec, loader):
        ...    # return ValueSupplierInterface from spec config
    """
    types = catalogue.create('datagen', 'type')
    schemas = catalogue.create('datagen', 'schemas')
    preprocessors = catalogue.create('datagen', 'preprocessor')
    logging = catalogue.create('datagen', 'logging')
    formats = catalogue.create('datagen', 'format')
    distribution = catalogue.create('datagen', 'distribution')
    defaults = catalogue.create('datagen', 'defaults')


def lookup_type(key):
    """
    Looks up the type in the registry

    Args:
        key: for type to look up

    Returns:
        the type if found
    """
    return registry.types.get(key)


def lookup_schema(key):
    """
    Looks up the schema in the registry

    Args:
        key: for schema to look up

    Returns:
        the schema if found
    """
    all_keys = list(registry.schemas.get_all().keys())
    if key in all_keys:
        schema_load_function = registry.schemas.get(key)
    else:
        log.debug('No schema found for type %s', key)
        return None

    return schema_load_function()


def valid_formats():
    """ list of registered formats """
    return list(registry.formats.get_all().keys())


def get_default(key):
    """
    get the default value for the specified key

    Args:
        key: to lookup

    Returns:
        The default for thekey
    """

    func = registry.defaults.get(key)
    return func()


def set_default(key: str, value: Any):
    """
    set the default value for the given key in the registry

    Args:
        key: to set default for
        value: for the default
    """
    registry.defaults.register(name=key, func=lambda *_: value)


def all_defaults():
    """ creates a dictionary of the current state of the registered defaults """
    return {k: get_default(k) for k in registry.defaults.get_all()}
