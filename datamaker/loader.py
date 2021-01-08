import json
import datamaker.suppliers as suppliers
from datamaker.exceptions import SpecException
import datamaker.types as types


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
        self.specs = specs
        self.cache = {}
        if 'refs' in specs:
            self.refs = Refs(specs.get('refs'))
        else:
            self.refs = None

    def get(self, key):
        """
        Retrieve the value supplier for the given field key
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
            return suppliers.values(data_spec)

        handler = types.lookup_type(spec_type)
        if handler is None:
            raise SpecException('Unable to load handler for: ' + json.dumps(data_spec))
        supplier = handler(data_spec, self)
        if suppliers.isdecorated(data_spec):
            return suppliers.decorated(data_spec, supplier)
        return supplier
