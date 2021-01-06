import json
from datamaker import suppliers
from datamaker import SpecException


def configure_supplier(data_spec, loader):
    key_supplier = suppliers.values(data_spec)
    values_map = {}
    for key, weight in data_spec['data'].items():
        field_spec = loader.refs.get(key)
        supplier = loader.get_from_spec(field_spec)
        if supplier is None:
            raise SpecException("Unable to get supplier for ref key: %s, spec: %s" % (key, json.dumps(field_spec)))
        values_map[key] = supplier
    return suppliers.weighted_ref(key_supplier, values_map)
