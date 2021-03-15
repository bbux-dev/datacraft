from dataspec import registry
import dataspec.schemas as schemas

VALUES_KEY = 'values'


@registry.schemas(VALUES_KEY)
def get_schema():
    return schemas.load(VALUES_KEY)
