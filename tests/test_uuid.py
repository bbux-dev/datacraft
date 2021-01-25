import re
from dataspec.loader import Loader
# need this to trigger registration
from dataspec.type_handlers import uuid_handler


UUID_REGEX = re.compile('[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', re.I)


def test_uuid_spec():
    spec = {"foo": {"type": "uuid"}}

    loader = Loader(spec)
    supplier = loader.get('foo')

    value1 = supplier.next(0)
    assert UUID_REGEX.match(value1)
    value2 = supplier.next(1)
    assert UUID_REGEX.match(value2)

    assert value1 != value2
