"""
Loader module is the interface into the dataspec data generation utility.  This class handles loading, parsing and
delegating the handling of various data types.
"""

import json
import dataspec.suppliers as suppliers
from dataspec.exceptions import SpecException
import dataspec.types as types
# need to make sure the default one is registered
from .preprocessor import *


class Refs:
    """
    Holder object for references
    """

    def __init__(self, refspec):
        if refspec:
            self.refspec = refspec
        else:
            self.refspec = {}

    def get(self, key):
        return self.refspec.get(key)


class Loader:
    """
    Parent object for loading value suppliers from specs
    """

    def __init__(self, specs, datadir='./data'):
        self.specs = _preprocess_spec(specs)
        self.datadir = datadir
        self.cache = {}
        self.refs = Refs(self.specs.get('refs'))

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

    def get_from_spec(self, field_spec):
        """
        Retrieve the value supplier for the given field spec
        """
        if isinstance(field_spec, list):
            spec_type = None
        else:
            spec_type = field_spec.get('type')

        if spec_type == 'configref':
            raise SpecException(f'Cannot use configref as source of data: {json.dumps(field_spec)}')
        if spec_type is None or spec_type == 'values':
            supplier = suppliers.values(field_spec)
        else:
            handler = types.lookup_type(spec_type)
            if handler is None:
                raise SpecException('Unable to load handler for: ' + json.dumps(field_spec))
            supplier = handler(field_spec, self)

        if suppliers.isdecorated(field_spec):
            return suppliers.decorated(field_spec, supplier)
        return supplier


def _preprocess_spec(raw_spec):
    updated = dict(raw_spec)
    preprocessors = types.registry.preprocessors.get_all()
    for name in preprocessors:
        preprocessor = types.registry.preprocessors.get(name)
        updated = preprocessor(updated)
    return updated
