""" Module to gather usage info from registered types """
import logging

from . import registries

_TYPE_BREAK = '-------------------------------------'

_log = logging.getLogger(__name__)


def build_cli_help(included_types: list = None):
    """Builds the command line interface help from the registered usage

    Args:
        included_types: list of type to include, default is to include all

    Returns:
        Formatted usage string from types
    """
    if included_types is None:
        included_types = registries.registered_types()
    usage_keys = registries.registered_usage()

    width = max(len(key) for key in included_types)

    entries = [_TYPE_BREAK]
    for type_key in included_types:
        if type_key in usage_keys:
            func = registries.Registry.usage.get(type_key)
            description = func()

            entries.append(f'{type_key.ljust(width)} | {description}')
        else:
            entries.append(f'{type_key.ljust(width)} | no usage defined')
        entries.append(_TYPE_BREAK)
    return '\n'.join(entries)
