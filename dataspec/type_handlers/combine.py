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
from dataspec import registry, suppliers, SpecException
from dataspec.suppliers import from_list_of_suppliers
import dataspec.schemas as schemas

COMBINE_KEY = 'combine'
COMBINE_LIST_KEY = 'combine-list'


@registry.schemas(COMBINE_KEY)
def get_combine_schema():
    return schemas.load(COMBINE_KEY)


@registry.schemas(COMBINE_LIST_KEY)
def get_combine_list_schema():
    return schemas.load(COMBINE_LIST_KEY)


@registry.types(COMBINE_KEY)
def configure_combine_supplier(field_spec, loader):
    """ configures supplier for combine type """
    if 'refs' not in field_spec and 'fields' not in field_spec:
        raise SpecException('Must define one of fields or refs. %s' % json.dumps(field_spec))

    if 'refs' in field_spec:
        supplier = _load_from_refs(field_spec, loader)
    else:
        supplier = _load_from_fields(field_spec, loader)
    return supplier


@registry.types(COMBINE_LIST_KEY)
def configure_combine_list_supplier(field_spec, loader):
    """ configures supplier for combine-list type """
    if 'refs' not in field_spec:
        raise SpecException('Must define refs for combine-list type. %s' % json.dumps(field_spec))

    refs_list = field_spec['refs']
    if len(refs_list) < 1 or not isinstance(refs_list[0], list):
        raise SpecException('refs pointer must be list of lists: i.e [["ONE", "TWO"]]. %s' % json.dumps(field_spec))

    suppliers_list = []
    for ref in refs_list:
        spec = dict(field_spec)
        spec['refs'] = ref
        suppliers_list.append(_load_from_refs(spec, loader))
    return from_list_of_suppliers(suppliers_list, True)


def _load_from_refs(combine_field_spec, loader):
    keys = combine_field_spec.get('refs')
    to_combine = []
    for key in keys:
        supplier = loader.get(key)
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
