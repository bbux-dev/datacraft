"""
module to handle ref specs

formats supported:

{ "field": { "data": "ref_name" } }, "refs": { "ref_name": 42 } }

{ "field": { "ref": "ref_name" } }, "refs": { "ref_name": 42 } }

"""
import json
import dataspec


@dataspec.registry.types('ref')
def configure_ref_supplier(field_spec: dict, loader: dataspec.Loader):
    """ configures supplier for ref type """
    key = None
    if 'data' in field_spec:
        key = field_spec.get('data')
    if 'ref' in field_spec:
        key = field_spec.get('ref')
    if key is None:
        raise dataspec.SpecException('No key found for spec: ' + json.dumps(field_spec))
    return loader.get(key)
