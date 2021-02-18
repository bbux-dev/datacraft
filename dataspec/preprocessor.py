"""
Module for preprocessing spec before generating values. Exists to handle shorthand notation and
pushing params from URL form of field?param=value in to config object.
"""
import json
from urllib.parse import urlparse
from urllib.parse import parse_qs
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
    newkey, spectype, params = _parse_key(key)

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
    config.update(params)
    updated['config'] = config
    if spectype:
        updated['type'] = spectype

    updated_specs[newkey] = updated


def _parse_key(field_name):
    """
    Expected key to have URL format. Two main forms:
    1. field:field_type?param1=val&param2=val...
    2. field?param1=val...
    """
    parsed_url = urlparse(field_name)
    parsed_query = parse_qs(parsed_url.query)
    if parsed_url.scheme:
        newkey = parsed_url.scheme
        spectype = parsed_url.path
    else:
        # case that the key portion has non standard chars such as _
        if ':' in parsed_url.path:
            newkey, spectype = parsed_url.path.split(':', 2)
        else:
            newkey = parsed_url.path
            spectype = None
    config = {}
    for key, value in parsed_query.items():
        if len(value) == 1:
            config[key] = value[0]
        else:
            config[key] = value

    return newkey, spectype, config


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
            spec = {
                'type': spectype,
                'data': spec
            }
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
    for core_field in ['type', 'data', 'config', 'ref', 'refs', 'fields']:
        if core_field in spec:
            return False
    # if empty, then may be using abbreviated notation i.e. field:type?param=value...
    if len(spec) == 0:
        return False
    # didn't find any core fields, and spec is not empty, so this must be data
    return True
