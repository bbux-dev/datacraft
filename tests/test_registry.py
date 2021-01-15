import dataspec
from dataspec import suppliers
from dataspec.loader import Loader
import dataspec.types as types


spec = {
    'foo': {
        'type': 'reverse_string',
        'ref': 'ONE'
    },
    'refs': {
        'ONE': {'type': 'values', 'data': ['raed a eod']}
    }
}


class ReverseStringSupplier:
    def __init__(self, wrapped):
        self.wrapped = wrapped

    def next(self, iteration):
        value = str(self.wrapped.next(iteration))
        return value[::-1]


@dataspec.registry.types('reverse_string')
def configure_supplier(field_spec, loader):
    key = field_spec.get('ref')
    myspec = loader.refs.get(key)
    wrapped = suppliers.values(myspec)
    return ReverseStringSupplier(wrapped)


def test_registry():
    loader = Loader(spec)

    reg = types.registry
    all_types = reg.types.get_all()
    handler = all_types.get('reverse_string')

    supplier = handler(spec.get('foo'), loader)

    assert supplier.next(0) == 'doe a dear'

