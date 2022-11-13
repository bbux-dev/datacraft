""" Module to gather usage info from registered types """
import logging

from . import registries, entrypoints

_TYPE_BREAK = '-------------------------------------'

_log = logging.getLogger(__name__)


def build_cli_help(*included_types):
    """Builds the command line interface help from the registered usage

    Args:
        included_types: *args of types to include, default is to include all

    Returns:
        Formatted usage string from types
    """
    # trigger any custom code loading
    entrypoints.load_eps()
    return _build_help('cli', *included_types)


def build_api_help(*included_types):
    """Builds the API help from the registered usage

    Args:
        included_types: *args of types to include, default is to include all

    Returns:
        Formatted usage string from types
    """
    # trigger any custom code loading
    entrypoints.load_eps()
    return _build_help('api', *included_types)


def _build_help(help_type: str, *included_types):
    registered_types = registries.registered_types()
    if included_types is None or len(included_types) == 0:
        included_types = registered_types
    usage_keys = registries.registered_usage()

    width = max(len(key) for key in included_types)  # type: ignore

    entries = [_TYPE_BREAK]
    for type_key in included_types:  # type: ignore
        if type_key in usage_keys:
            func = registries.Registry.usage.get(type_key)
            description = func()
            if isinstance(description, dict):
                description = description.get(help_type, f'no {help_type} usage defined')

            entries.append(f'{type_key.ljust(width)} | {description}')
        elif type_key not in registered_types:
            entries.append(f'{type_key.ljust(width)} | unknown type')
        else:
            entries.append(f'{type_key.ljust(width)} | no usage defined')
        entries.append(_TYPE_BREAK)
    return '\n'.join(entries)