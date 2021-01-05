import json
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

        data = self.specs.get(key)
        if data is None:
            raise SpecException("No key " + key + " found in specs")
        if 'type' not in data:
            raise SpecException('No type defined for: ' + str(data))
        return self.get_from_spec(data)

    def get_from_spec(self, data):
        """
        Retrieve the value supplier for the given field spec
        """
        if data['type'] == 'values':
            return suppliers.values(data)
        if data['type'] == 'combine':
            if not self.refs:
                raise SpecException("No refs element defined in specification!" + str(self.specs))
            keys = data.get('refs')
            to_combine = []
            for key in keys:
                field_spec = self.refs.get(key)
                supplier = self.get_from_spec(field_spec)
                if supplier is None:
                    raise SpecException("Unable to get supplier for ref key: %s, spec: %s" % (key, json.dumps(field_spec)))
                to_combine.append(supplier)
            return suppliers.combine(to_combine, data.get('config'))
        if data['type'] == 'weightedref':
            key_supplier = suppliers.weighted_values(data)
            values_map = {}
            for key, weight in data['data'].items():
                field_spec = self.refs.get(key)
                supplier = self.get_from_spec(field_spec)
                if supplier is None:
                    raise SpecException("Unable to get supplier for ref key: %s, spec: %s" % (key, json.dumps(field_spec)))
                values_map[key] = supplier
            return suppliers.weighted_ref(key_supplier, values_map)
