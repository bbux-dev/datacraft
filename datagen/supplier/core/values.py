"""
Module for values types
"""

import datagen

_VALUES_KEY = 'values'


@datagen.registry.schemas(_VALUES_KEY)
def _get_schema():
    """ returns the values schema """
    return datagen.schemas.load(_VALUES_KEY)
