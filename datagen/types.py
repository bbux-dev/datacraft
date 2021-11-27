"""
Module for the datagen registration system
"""
import logging
from typing import Any

import catalogue  # type: ignore

_log = logging.getLogger(__name__)


class registry:
    """
    Catalogue registry for types, preprocessors, logging configuration, and others

    Attributes:
        types:
            Types for field specs, registered functions for creating ValueSupplierInterface that will supply
            values for the given type

            >>> @datagen.registry.types('special_sauce')
            ... def _handle_special_type(field_spec: dict, loader: datagen.Loader) -> datagen.ValueSupplierInterface:
            ...    # return ValueSupplierInterface from spec config

        schemas:
            Schemas for field spec types, used to validate that the spec for a given type conforms to the schema
            for it

            >>> @datagen.registry.schemas('special_sauce')
            ... def _special_sauce_schema() -> dict:
            ...    # return JSON schema validating specs with type: special_sauce

        preprocessors:
            Functions to modify specs before data generations process. If there is a customization you want to do for
            every data spec, or an extenstion you added that requires modifications to the spec before they are run,
            this is where you would register that pre-processor.

            >>> @datagen.registry.preprocessors('custom-preprocessing')
            ... def _preprocess_spec_to_some_end(raw_spec: dict) -> dict:
            ...    # return spec with any modification

        logging:
            Custom logging setup. Can override or modify the default logging behavior.

            >>> @datagen.registry.logging('denoise')
            ... def _customize_logging(loglevel: str):
            ...     logging.getLogger('too.verbose.module').level = logging.ERROR

        formats:
            Registered formats for output.  When using the --format <format name>. Unlike other registered functions,
            this one is called directly for to perform the required formatting function. The return value from the
            formatter is the new value that will be written to the configured output (default is console).

            >>> @datagen.registry.formats('custom_format')
            ... def _format_custom(record: dict) -> str:
            ...     # write to database or some other custom output, return something to write out or print to console

        distribution:
            Different numeric distributions, normal, uniform, etc. These are used for more nuanced counts values. The
            built in distributions are uniform and normal.

            >>> @datagen.registry.distribution('hyperbolic_inverse_haversine')
            ... def _hyperbolic_inverse_haversine(mean, stddev, **kwargs):
            ...     # return a datagen.Distribution, args can be custom for the defined distribution

        defaults:
            Default values. Different types have different default values for some configs.  This provides a mechanism
            to override or to register other custom defaults. Read a default from the registry
            with: ``datagen.types.get_default('var_key')``. While ``datagen.types.all_defaults()`` will give a mapping
            of all registered default keys and values.

            >>> @datagen.registry.defaults('special_sauce_ingredient')
            ... def _default_special_sauce_ingredient():
            ...     # return the default value (i.e. onions)

        casters:
            Cast or alter values in simple ways. These are all the valid forms of altering generated values after they
            are created outside of the ValueSupplier types. Use ``datagen.types.registered_casters()`` to get a list
            of all the currently registered ones.

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
    all_keys = list(registry.types.get_all().keys())
    if key in all_keys:
        func = registry.types.get(key)
    else:
        _log.debug('No schema found for type %s', key)
        return None

    return func


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
        _log.debug('No schema found for type %s', key)
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
        _log.debug('No caster found for type %s', key)
        return None

    return caster_load_function()


def registered_formats():
    """ list of registered formats """
    return list(registry.formats.get_all().keys())


def registered_types():
    """ list of registered types """
    return list(registry.types.get_all().keys())


def registered_casters():
    """ list of registered casters """
    return list(registry.casters.get_all().keys())


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
