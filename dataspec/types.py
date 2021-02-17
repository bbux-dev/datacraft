"""
Module for the dataspec registration system
"""
import catalogue


class registry:
    """
    Catalogue registry for types, preprocessors, and logging configuration
    """
    types = catalogue.create('dataspec', 'type')
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


def valid_formats():
    return list(registry.formats.get_all().keys())