import uuid
import dataspec


class UuidSupplier:
    def next(self, _):
        return str(uuid.uuid4())


@dataspec.registry.types('uuid')
def configure_supplier(_, __):
    return UuidSupplier()
