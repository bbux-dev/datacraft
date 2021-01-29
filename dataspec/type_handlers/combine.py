"""
Combine handler builds a combine value supplier from the provided spec

A combine Field Spec is used to concatenate or append two or more fields or reference to one another.
The combine field structure is:
{
  "<field name>": {
    "type": "combine",
    "fields": ["valid field name1", "valid field name2"],
    OR
    "refs": ["valid ref1", "valid ref2"],
    "config": { "join_with": "<optional string to use to join fields or refs, default is none"}
  }
}
"""
import json
import dataspec
from dataspec import SpecException, suppliers


@dataspec.registry.types('combine')
def configure_supplier(field_spec, loader):
    if 'refs' not in field_spec and 'fields' not in field_spec:
        raise SpecException('Must define one of fields or refs. %s' % json.dumps(field_spec))

    if 'refs' in field_spec:
        supplier = _load_from_refs(field_spec, loader)
    else:
        supplier = _load_from_fields(field_spec, loader)
    return supplier


def _load_from_refs(combine_field_spec, loader):
    keys = combine_field_spec.get('refs')
    to_combine = []
    for key in keys:
        field_spec = loader.refs.get(key)
        if field_spec is None:
            raise SpecException("Unable to get field_spec for ref key: %s, spec: %s" % (key, json.dumps(combine_field_spec)))
        supplier = loader.get_from_spec(field_spec)
        if supplier is None:
            raise SpecException("Unable to get supplier for ref key: %s, spec: %s" % (key, json.dumps(field_spec)))
        to_combine.append(supplier)
    return suppliers.combine(to_combine, combine_field_spec.get('config'))


def _load_from_fields(data_spec, loader):
    keys = data_spec.get('fields')
    to_combine = []
    for key in keys:
        supplier = loader.get(key)
        if supplier is None:
            raise SpecException("Unable to get supplier for field key: %s" % key)
        to_combine.append(supplier)
    return suppliers.combine(to_combine, data_spec.get('config'))
