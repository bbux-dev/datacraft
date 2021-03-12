import dataspec
import dataspec.schemas as schemas

VALUES_KEY = 'values'


@dataspec.registry.schemas(VALUES_KEY)
def get_schema():
    return schemas.load(VALUES_KEY)
