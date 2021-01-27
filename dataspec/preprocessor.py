"""
Module for preprocessing spec before generating values. Exists to handle shorthand notation and
pushing params from URL form of field?param=value in to config object.
"""
import json
import dataspec
from .exceptions import SpecException


@dataspec.registry.preprocessors('default')
def preprocess_spec(raw_spec):
    """
    Preprocesses the spec into a format that is easier to use.
    Pushes all url params in keys into config object. Converts shorthand specs into full specs
    :param raw_spec: to preprocess
    :return: the reformatted spec
    """
    updated_specs = {}
    for key, spec in raw_spec.items():
        if '?' not in key:
            _update_no_params(key, spec, updated_specs)
        else:
            _update_with_params(key, spec, updated_specs)
    if 'refs' in raw_spec:
        updated_specs['refs'] = preprocess_spec(raw_spec['refs'])
    return updated_specs


def _update_with_params(key, spec, updated_specs):
    """
    handles the case that there are ?param=value portions in the key
    These get stripped out and pushed into the config object
    """
    if ' ' in key:
        raise SpecException(f'Invalid url key {key}, no spaces allowed')
    newkey, params = key.replace('?', ' ').split(' ', 2)
    if ':' in newkey:
        newkey, spectype = newkey.split(':', 2)
        if not _is_spec_data(spec):
            spec['type'] = spectype
    if newkey in updated_specs:
        raise SpecException(f'Field {key} defined multiple times: ' + json.dumps(spec))
    # the updated spec to populate
    updated = {}

    if _is_spec_data(spec):
        updated['data'] = spec
    else:
        # copy all existing values
        updated.update(spec)

    config = updated.get('config', {})

    for param in params.split('&'):
        keyvalue = param.split('=')
        config[keyvalue[0]] = keyvalue[1]
    updated['config'] = config

    updated_specs[newkey] = updated


def _update_no_params(key, spec, updated_specs):
    """
    handles the case when there are no ?param=value portions in the key
    key may have name:type notation that still needs to be handled
    """
    if ':' in key:
        newkey, spectype = key.split(':', 2)
        if not _is_spec_data(spec):
            spec['type'] = spectype
    else:
        newkey = key
    # check for conflicts
    if key in updated_specs:
        raise SpecException(f'Field {key} defined multiple times: ' + json.dumps(spec))
    updated_specs[newkey] = spec


def _is_spec_data(spec):
    """
    Checks to see if the spec is data only
    :return: true if only data, false if it is a spec
    """
    # if it is not a dictionary, then it is definitely not a spec
    if not isinstance(spec, dict):
        return True
    for core_field in ['type', 'data', 'config']:
        if core_field in spec:
            return False
    # if empty, then may be using abbreviated notation i.e. field:type?param=value...
    if len(spec) == 0:
        return False
    # didn't find any core fields, and spec is not empty, so this must be data
    return True
