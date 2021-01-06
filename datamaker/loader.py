import datamaker.suppliers as suppliers
from datamaker.exceptions import SpecException


class Refs(object):
    """
    Holder object for references
    """
    def __init__(self, refspec):
        self.refspec = refspec

    def get(self, key):
        return self.refspec.get(key)


class Loader(object):
    """
    Parent object for loading value suppliers from specs
    """
    def __init__(self, specs, registry):
        self.specs = specs
        self.registry = registry
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
        if 'type' not in data_spec:
            raise SpecException('No type defined for: ' + str(data_spec))
        return self.get_from_spec(data_spec)

    def get_from_spec(self, data_spec):
        """
        Retrieve the value supplier for the given field spec
        """
        if isinstance(data_spec, list):
            type = None
        else:
            type = data_spec.get('type')

        if type is None or type == 'values':
            return suppliers.values(data_spec)

        return self.registry.lookup(type).configure_supplier(data_spec, self)

