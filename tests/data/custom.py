import datacraft


class StringReverserSupplier:
    def __init__(self, wrapped):
        self.wrapped = wrapped

    def next(self, iteration):
        value = str(self.wrapped.next(iteration))
        return value[::-1]


@datacraft.registry.types('string_reverser')
def configure_supplier(field_spec, loader):
    key = field_spec.get('ref')
    wrapped = loader.get(key)
    return StringReverserSupplier(wrapped)
