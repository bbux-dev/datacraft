"""
Module for classes and function to support calculate type
"""
import json
import logging
import asteval  # type: ignore

from .exceptions import SpecException
from .supplier.calculate import calculate_supplier
from .loader import Loader
from . import types, schemas, template_engines

_log = logging.getLogger(__name__)


@types.registry.schemas('calculate')
def _calculate_schema():
    """ get the schema for the calculate type """
    return schemas.load('calculate')


@types.registry.types('calculate')
def _configure_calculate_supplier(field_spec: dict, loader: Loader):
    """ configures supplier for calculate type """
    if 'refs' not in field_spec and 'fields' not in field_spec:
        raise SpecException('Must define one of fields or refs. %s' % json.dumps(field_spec))
    if 'refs' in field_spec and 'fields' in field_spec:
        raise SpecException('Must define only one of fields or refs. %s' % json.dumps(field_spec))
    template = field_spec.get('formula')
    if template is None:
        raise SpecException('Must define formula for calculate type. %s' % json.dumps(field_spec))

    mappings = _get_mappings(field_spec, 'refs')
    mappings.update(_get_mappings(field_spec, 'fields'))

    if len(mappings) < 1:
        raise SpecException('fields or refs empty: %s' % json.dumps(field_spec))

    suppliers = {}
    for field_or_ref, alias in mappings.items():
        supplier = loader.get(field_or_ref)
        suppliers[alias] = supplier

    engine = template_engines.string(template)
    return calculate_supplier(suppliers=suppliers, engine=engine)


def _get_mappings(field_spec, key):
    """ retrieve the field aliasing for the given key, refs or fields """
    mappings = field_spec.get(key, [])
    if isinstance(mappings, list):
        mappings = {key: key for key in mappings}
    return mappings
