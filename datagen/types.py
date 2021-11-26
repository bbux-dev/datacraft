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
        types: types for field specs

            >>> @datagen.registry.types('special_sauce')
            ... def _handle_special_type(field_spec: dict, loader: datagen.Loader):
            ...    # return ValueSupplierInterface from spec config

        schemas: schemas for field spec types

            >>> @datagen.registry.schemas('special_sauce')
            ... def _special_sauce_schema():
            ...    # return JSON schema validating specs with type: special_sauce

        preprocessors: functions to modify specs before running

            >>> @datagen.registry.preprocessors('custom-preprocessing')
            ... def _preprocess_spec_to_some_end(raw_spec: dict):
            ...    # return spec with any modification

        logging: custom logging setup

            >>> @datagen.registry.logging('denoise')
            ... def _customize_logging(loglevel: str):
            ...     logging.getLogger('too.verbose.module').level = logging.ERROR

        formats: registered formats for output

            >>> @datagen.registry.formats('custom_format')
            ... def _format_custom(record: dict) -> str:
            ...     # write to database or some other custom output, return something to write out or print to console

        distribution: different numeric distributions, normal, uniform, etc

            >>> @datagen.registry.distribution('hyperbolic_inverse_haversine')
            ... def _hyperbolic_inverse_haversine(mean, stddev, **kwargs):
            ...     # return a datagen.Distribution, args can be custom for the defined distribution

        defaults: default values

            >>> @datagen.registry.defaults('special_sauce_ingredient')
            ... def _default_special_sauce_ingredient():
            ...     # return the default value (i.e. onions)

        casters: cast or alter values in simple ways

            >>> @datagen.registry.casters('reverse')
            ... def _cast_reverse_strings():
            ...     # return a datagen.CasterInterface

    """
    types = catalogue.create('datagen', 'type')
    schemas = catalogue.create('datagen', 'schemas')
    preprocessors = catalogue.create('datagen', 'preprocessor')
    logging = catalogue.create('datagen', 'logging')
    formats = catalogue.create('datagen', 'format')
    distribution = catalogue.create('datagen', 'distribution')
    defaults = catalogue.create('datagen', 'defaults')
    casters = catalogue.create('datagen', 'casters')


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


def lookup_caster(key):
    """
    Looks up the caster in the registry

    Args:
        key: for caster to look up

    Returns:
        the caster if found
    """
    all_keys = list(registry.casters.get_all().keys())
    if key in all_keys:
        caster_load_function = registry.casters.get(key)
    else:
        log.debug('No caster found for type %s', key)
        return None

    return caster_load_function()


def registered_formats():
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
