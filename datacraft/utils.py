"""
Module for storing package wide common functions
"""
import importlib
import logging
import os
from typing import Union

from .supplier.model import DataSpec
from .exceptions import ResourceError


# not code hinted type, due to mypy issue recognising importlib.util
def load_custom_code(code_path):
    """
    Loads user custom code

    Args:
        code_path: path to the custom code to load
    """
    if not os.path.exists(code_path):
        raise FileNotFoundError(f'Path to {code_path} not found.')
    code_spec = importlib.util.spec_from_file_location("python_code", str(code_path))
    if code_spec is None:
        raise ResourceError(f"Couldn't load custom Python code from: {code_path}")
    try:
        module = importlib.util.module_from_spec(code_spec)
        code_spec.loader.exec_module(module)
    except Exception as exc:
        logging.warning("Couldn't load custom Python code: %s: %s", code_path, str(exc))
        raise ResourceError(f"Couldn't load custom Python code: {code_path}: {exc}") from exc


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


def load_config(field_spec: dict, loader, **kwargs) -> dict:
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
    refkey = config.get('config_ref')
    if refkey:
        config_ref = loader.get_ref(refkey)
        config.update(config_ref.get('config', {}))
    return config


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


def any_is_float(data):
    """ are any of the items floats """
    for item in data:
        if isinstance(item, float):
            return True
    return False


def decode_num(num):
    """ decodes the num if hex encoded """
    if isinstance(num, str):
        return int(num, 16)
    return int(num)


def load_file_as_string(data_path: str) -> str:
    """ Loads the file at the given path as a string"""
    with open(data_path, 'r', encoding='utf-8') as handle:
        return handle.read()
