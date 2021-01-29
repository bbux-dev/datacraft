import dataspec


class StringReverserSupplier:
    def __init__(self, wrapped):
        self.wrapped = wrapped

    def next(self, iteration):
        value = str(self.wrapped.next(iteration))
        return value[::-1]


@dataspec.registry.types('string_reverser')
def configure_supplier(field_spec, loader):
    key = field_spec.get('ref')
    myspec = loader.refs.get(key)
    wrapped = loader.get_from_spec(myspec)
    return StringReverserSupplier(wrapped)
