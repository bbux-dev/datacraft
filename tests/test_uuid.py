import re

import pytest

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


valid_data_specs = [
    ("foo:uuid", {}),
    ("foo:uuid", {"config": {"variant": 1}}),
    ("foo:uuid", {"config": {"variant": 3}}),
    ("foo:uuid", {"config": {"variant": 4}}),
    ("foo:uuid", {"config": {"variant": 5}}),
]


@pytest.mark.parametrize("key,spec", valid_data_specs)
def test_uuid_valid_schema(key, spec):
    # for coverage
    spec = builder.single_field(key, spec).build()
    loader = Loader(spec, enforce_schema=True)
    supplier = loader.get('foo')

    value1 = supplier.next(0)
    assert UUID_REGEX.match(value1)
