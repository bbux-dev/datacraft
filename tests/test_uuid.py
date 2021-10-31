import re
from datagen import builder, Loader
# need this to trigger registration
from datagen.supplier.core import uuid_handler


UUID_REGEX = re.compile('[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', re.I)


def test_uuid_spec():
    spec = builder.single_field("foo:uuid", {}).build()
    loader = Loader(spec)
    supplier = loader.get('foo')

    value1 = supplier.next(0)
    assert UUID_REGEX.match(value1)
    value2 = supplier.next(1)
    assert UUID_REGEX.match(value2)

    assert value1 != value2


def test_uuid_schema():
    # for coverage
    spec = builder.single_field("foo:uuid", {}).build()
    loader = Loader(spec, enforce_schema=True)
    supplier = loader.get('foo')

    value1 = supplier.next(0)
    assert UUID_REGEX.match(value1)
