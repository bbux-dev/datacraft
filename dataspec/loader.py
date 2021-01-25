import json
import dataspec.suppliers as suppliers
from dataspec.exceptions import SpecException
import dataspec.types as types


class Refs:
    """
    Holder object for references
    """

    def __init__(self, refspec):
        self.refspec = refspec

    def get(self, key):
        return self.refspec.get(key)


class Loader:
    """
    Parent object for loading value suppliers from specs
    """

    def __init__(self, specs):
        self.specs = _preprocess_spec(specs)
        self.cache = {}
        if 'refs' in specs:
            self.refs = Refs(self.specs.get('refs'))
        else:
            self.refs = None

    def get(self, key):
        """
        Retrieve the value supplier for the given field key

        :param key: key to use, may have url format i.e. field_name?param=value...
        """
        if key in self.cache:
            return self.cache[key]

        data_spec = self.specs.get(key)
        if data_spec is None:
            raise SpecException("No key " + key + " found in specs")
        return self.get_from_spec(data_spec)

    def get_from_spec(self, data_spec):
        """
        Retrieve the value supplier for the given field spec
        """
        if isinstance(data_spec, list):
            spec_type = None
        else:
            spec_type = data_spec.get('type')

        if spec_type is None or spec_type == 'values':
            supplier = suppliers.values(data_spec)
        else:
            handler = types.lookup_type(spec_type)
            if handler is None:
                raise SpecException('Unable to load handler for: ' + json.dumps(data_spec))
            supplier = handler(data_spec, self)

        if suppliers.isdecorated(data_spec):
            return suppliers.decorated(data_spec, supplier)
        return supplier


def _preprocess_spec(raw_spec):
    """
    Preprocesses the spec into a format that is easier to use.
    Pushes all url params in keys into config object. Converts shorthand specs into full specs
    :param raw_spec: to preprocess
    :return: the reformatted spec
    """
    updated_specs = {}
    for key, spec in raw_spec.items():
        if '?' not in key:
            # check for conflicts
            if key in updated_specs:
                raise SpecException(f'Field {key} defined multiple times: ' + json.dumps(spec))
            updated_specs[key] = spec
        else:
            if ' ' in key:
                raise SpecException(f'Invalid url key {key}, no spaces allowed')
            newkey, params = key.replace('?', ' ').split(' ', 2)
            if newkey in updated_specs:
                raise SpecException(f'Field {key} defined multiple times: ' + json.dumps(spec))
            # the updated spec to populate
            updated = {}

            if _is_spec_data(spec):
                updated['data'] = spec
            else:
                # copy all existing values
                updated.update(spec)

            if 'config' in updated:
                config = updated['config']
            else:
                config = {}
            for param in params.split('&'):
                keyvalue = param.split('=')
                config[keyvalue[0]] = keyvalue[1]
            updated['config'] = config

            updated_specs[newkey] = updated
    if 'refs' in raw_spec:
        updated_specs['refs'] = _preprocess_spec(raw_spec['refs'])
    return updated_specs


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
    # didn't find any core fields, so this must be data
    return True

