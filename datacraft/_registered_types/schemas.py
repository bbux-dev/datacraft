import json
import logging

from . import common
import importlib_resources as pkg_resources


from . import schema

_log = logging.getLogger(__name__)


def load_resource_as_json(resource_name: str) -> dict:
    """ loads the internal json resource with the given resource_name """
    try:
        with pkg_resources.open_text(schema, resource_name) as schema_resource:
            return json.load(schema_resource)
    except FileNotFoundError as err:
        from datacraft import ResourceError
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
    return load_resource_as_json(naming_convention)
