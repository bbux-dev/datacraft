import os
import importlib
import logging


def load_custom_code(code_path):
    """
    Loads user custom code
    :param code_path: path to the custom code to load
    :return: None
    """
    if not os.path.exists(code_path):
        raise Exception(f'Path to {code_path} not found.')
    try:
        spec = importlib.util.spec_from_file_location("python_code", str(code_path))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    except Exception as e:
        logging.warning(f"Couldn't load custom Python code: {code_path}: {e}")


def is_affirmative(key, config, default=False):
    value = str(config.get(key, default)).lower()
    return value in ['yes', 'true', 'on']


def load_config(field_spec, loader):
    if not isinstance(field_spec, dict):
        return {}

    config = field_spec.get('config', {})
    refkey = config.get('configref')
    if refkey:
        configref = loader.refs.get(refkey)
        config.update(configref.get('config', {}))
    return config
