import catalogue


class registry:
    types = catalogue.create('datamaker', 'type')


def lookup_type(key):
    return registry.types.get(key)
