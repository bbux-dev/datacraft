"""
Module for values type functionality
"""

from dataspec import registry
import dataspec.schemas as schemas

VALUES_KEY = 'values'


@registry.schemas(VALUES_KEY)
def get_schema():
    """ returns the values schema """
    return schemas.load(VALUES_KEY)
