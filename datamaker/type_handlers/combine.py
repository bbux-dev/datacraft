import json
from datamaker import suppliers
from datamaker import SpecException


def configure_supplier(data_spec, loader):
    if not loader.refs:
        raise SpecException("No refs element defined in specification!" + str(data_spec))
    keys = data_spec.get('refs')
    to_combine = []
    for key in keys:
        field_spec = loader.refs.get(key)
        supplier = loader.get_from_spec(field_spec)
        if supplier is None:
            raise SpecException("Unable to get supplier for ref key: %s, spec: %s" % (key, json.dumps(field_spec)))
        to_combine.append(supplier)
    return suppliers.combine(to_combine, data_spec.get('config'))
