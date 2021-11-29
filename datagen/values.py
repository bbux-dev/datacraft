"""
Module for values types
"""

from . import types, schemas

_VALUES_KEY = 'values'


@types.registry.schemas(_VALUES_KEY)
def _get_schema():
    """ returns the values schema """
    return schemas.load(_VALUES_KEY)
