"""module for schema loading for internal registered types"""
import json
import logging

import importlib_resources as pkg_resources

from datacraft import ResourceError

from . import schema

_log = logging.getLogger(__name__)


def load_resource_as_json(resource_name: str) -> dict:
    """ loads the internal json resource with the given resource_name """
    try:
        with (pkg_resources.files(schema) / resource_name).open('rb') as schema_resource:
            return json.load(schema_resource)
    except FileNotFoundError as err:
        raise ResourceError(f'No resource with name {resource_name} was found') from err


def load(key: str) -> dict:
    """
    load the internal schema file for the provided key

    Args:
        key: type name for schema

    Returns:
        Schema as dictionary for given key

    Raises:
        ResourceError if schema for key not found
    """
    naming_convention = f'{key}.schema.json'

    type_schema = load_resource_as_json(naming_convention)
    definitions = load_resource_as_json('definitions.json')
    if 'definitions' in type_schema:
        type_schema['definitions'].update(definitions['definitions'])
    else:
        type_schema['definitions'] = definitions['definitions']
    return type_schema
