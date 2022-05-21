import json

import datacraft


def _build_suppliers_map(field_spec, loader):
    if 'refs' not in field_spec and 'fields' not in field_spec:
        raise datacraft.SpecException('Must define one of fields or refs. %s' % json.dumps(field_spec))
    if 'refs' in field_spec and 'fields' in field_spec:
        raise datacraft.SpecException('Must define only one of fields or refs. %s' % json.dumps(field_spec))
    mappings = _get_mappings(field_spec, 'refs')
    mappings.update(_get_mappings(field_spec, 'fields'))
    if len(mappings) < 1:
        raise datacraft.SpecException('fields or refs empty: %s' % json.dumps(field_spec))
    suppliers_map = {}
    for field_or_ref, alias in mappings.items():
        supplier = loader.get(field_or_ref)
        suppliers_map[alias] = supplier
    return suppliers_map


def _get_mappings(field_spec, lookup_key):
    """ retrieve the field aliasing for the given key, refs or fields """
    mappings = field_spec.get(lookup_key, [])
    if isinstance(mappings, list):
        mappings = {_key: _key for _key in mappings}
    return mappings
