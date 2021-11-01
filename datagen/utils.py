"""
Module for storing package wide common functions
"""
from typing import Union
import os
import importlib
import logging

from . import casters
from .model import DataSpec


# not code hinted type, due to mypy issue recognising importlib.util
def load_custom_code(code_path):
    """
    Loads user custom code

    Args:
        code_path: path to the custom code to load
    """
    if not os.path.exists(code_path):
        raise FileNotFoundError(f'Path to {code_path} not found.')
    try:
        spec = importlib.util.spec_from_file_location("python_code", str(code_path))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    except Exception as exception:
        logging.warning("Couldn't load custom Python code: %s: %s", code_path, str(exception))


def is_affirmative(key: str, config: dict, default=False) -> bool:
    """
    Checks if the config value is one of true, yes, or on (case doesn't matter), default is False

    Args:
        key: to check
        config: to lookup key in
        default: if not found, False if not specified

    Returns:
        if the config is present and is one of true, yes, or on
    """
    value = str(config.get(key, default)).lower()
    return value in ['yes', 'true', 'on']


def load_config(field_spec: dict, loader, **kwargs):
    """
    Loads the config and any secondary configs into one object

    Args:
        field_spec: that should contain config
        loader: system spec loader

    Returns:
        the full config
    """
    if not isinstance(field_spec, dict):
        return kwargs

    config = field_spec.get('config', {})
    config.update(kwargs)
    refkey = config.get('configref')
    if refkey:
        configref = loader.get_ref_spec(refkey)
        config.update(configref.get('config', {}))
    return config


def get_caster(config: dict):
    """ returns the caster object from the config """
    return casters.get(config.get('cast'))


def any_key_exists(config: dict, keys: list):
    """ checks if any of the keys exist in the config object """
    return any(key in config for key in keys)


def get_raw_spec(data_spec: Union[dict, DataSpec]):
    """ The data spec may be raw or object version, this gets the raw underlying spec """
    if isinstance(data_spec, DataSpec):
        raw_spec = data_spec.raw_spec
    else:
        raw_spec = data_spec
    return raw_spec
