"""
Module for the dataspec registration system
"""
import logging
import catalogue

log = logging.getLogger(__name__)


class registry:
    """
    Catalogue registry for types, preprocessors, and logging configuration
    """
    types = catalogue.create('dataspec', 'type')
    schemas = catalogue.create('dataspec', 'schemas')
    preprocessors = catalogue.create('dataspec', 'preprocessor')
    logging = catalogue.create('dataspec', 'logging')
    formats = catalogue.create('dataspec', 'format')


def lookup_type(key):
    """
    Looks up the type in the registry
    :param key: for type to look up
    :return: the type if found
    """
    return registry.types.get(key)


def lookup_schema(key):
    """
    Looks up the schema in the registry
    :param key: for schema to look up
    :return: the schema if found
    """
    all_keys = list(registry.schemas.get_all().keys())
    if key in all_keys:
        schema_load_function = registry.schemas.get(key)
    else:
        log.debug('No schema found for type %s', key)
        return None

    return schema_load_function()


def valid_formats():
    return list(registry.formats.get_all().keys())