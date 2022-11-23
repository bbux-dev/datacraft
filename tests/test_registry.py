import json
import os

import pytest

import datacraft
import datacraft.registries as registries
from datacraft.utils import load_custom_code

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


@datacraft.registry.types('reverse_string')
def configure_supplier(field_spec, loader):
    key = field_spec.get('ref')
    wrapped = loader.get(key)
    return ReverseStringSupplier(wrapped)


@datacraft.registry.usage('reverse_string')
def get_reverse_string_usage():
    example = {
        "backwards": {
            "type": "reverse_string",
            "ref": "ANIMALS"
        },
        "refs": {
            "ANIMALS": {
                "type": "values",
                "data": ["zebra", "hedgehog", "llama", "flamingo"]
            }
        }
    }
    example_str = json.dumps(example, indent=4)
    command = 'datacraft -s spec.json -i 5 --format json-pretty -x -l off'
    output = json.dumps(datacraft.entries(example, 5, enforce_schema=True), indent=4)
    return '\n'.join([
        "Reverses output of other suppliers",
        "Example:", example_str,
        "Command:", command,
        "Output:", output
    ])


def test_registry_from_local():
    loader = datacraft.loader.field_loader(spec)

    reg = registries.Registry
    all_types = reg.types.get_all()
    handler = all_types.get('reverse_string')

    supplier = handler(spec.get('foo'), loader)

    assert supplier.next(0) == 'doe a dear'


def test_registry_from_file():
    # string_reverser, same as above just different key
    load_custom_code(os.path.join(test_dir, 'custom.py'))

    loader = datacraft.loader.field_loader(spec)

    reg = registries.Registry
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


class TestCaster(datacraft.CasterInterface):
    def cast(self, value):
        return value


@datacraft.registry.casters('test')
def _test_registered_caster():
    return TestCaster()


def test_lookup_caster():
    caster = registries.lookup_caster('test')
    assert caster is not None
    caster = registries.lookup_caster('not_registered')
    assert caster is None
    all_registered = registries.registered_casters()
    assert all_registered == ['test']
