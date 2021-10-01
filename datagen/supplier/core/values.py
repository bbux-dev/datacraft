"""
Module for values type functionality
"""

import datagen

VALUES_KEY = 'values'


@datagen.registry.schemas(VALUES_KEY)
def get_schema():
    """ returns the values schema """
    return datagen.schemas.load(VALUES_KEY)
