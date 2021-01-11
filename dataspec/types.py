import catalogue


class registry:
    types = catalogue.create('dataspec', 'type')


def lookup_type(key):
    return registry.types.get(key)
