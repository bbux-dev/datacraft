import os
import pytest
import datagen
from datagen.loader import Loader
import datagen.registries as registries
from datagen.utils import load_custom_code
from datagen import casters

spec = {
    'foo': {
        'type': 'reverse_string',
        'ref': 'ONE'
    },
    'refs': {
        'ONE': {'type': 'values', 'data': ['raed a eod']}
    }
}

test_dir = f'{os.path.dirname(os.path.realpath(__file__))}/data'


class ReverseStringSupplier:
    def __init__(self, wrapped):
        self.wrapped = wrapped

    def next(self, iteration):
        value = str(self.wrapped.next(iteration))
        return value[::-1]


@datagen.registry.types('reverse_string')
def configure_supplier(field_spec, loader):
    key = field_spec.get('ref')
    wrapped = loader.get(key)
    return ReverseStringSupplier(wrapped)


def test_registry_from_local():
    loader = Loader(spec)

    reg = registries.registry
    all_types = reg.types.get_all()
    handler = all_types.get('reverse_string')

    supplier = handler(spec.get('foo'), loader)

    assert supplier.next(0) == 'doe a dear'


def test_registry_from_file():
    # string_reverser, same as above just different key
    load_custom_code(os.path.join(test_dir, 'custom.py'))

    loader = Loader(spec)

    reg = registries.registry
    all_types = reg.types.get_all()
    handler = all_types.get('string_reverser')

    supplier = handler(spec.get('foo'), loader)

    assert supplier.next(0) == 'doe a dear'


def test_registry_error_case():
    with pytest.raises(FileNotFoundError):
        # string_reverser, same as above just different key
        load_custom_code(f'{test_dir}/custom_does_not_exist.py')


type_schema_key_lookup_tests = [
    ("uuid", True),
    ("values", True),
    ("spam", False),
    ("seaweed", False),
]


@pytest.mark.parametrize("key, should_exist", type_schema_key_lookup_tests)
def test_lookup_schema(key, should_exist):
    schema = registries.lookup_schema(key)
    if should_exist:
        assert schema is not None
    else:
        assert schema is None


@pytest.mark.parametrize("key, should_exist", type_schema_key_lookup_tests)
def test_lookup_type(key, should_exist):
    type_load_func = registries.lookup_type(key)
    if should_exist:
        assert type_load_func is not None
    else:
        assert type_load_func is None


class TestCaster(datagen.CasterInterface):
    def cast(self, value):
        return value


@datagen.registry.casters('test')
def _test_registered_caster():
    return TestCaster()


def test_lookup_caster():
    caster = registries.lookup_caster('test')
    assert caster is not None
    caster = registries.lookup_caster('not_registered')
    assert caster is None
    all_registered = registries.registered_casters()
    assert all_registered == ['test']
