import catalogue


class registry:
    types = catalogue.create('dataspec', 'type')
    preprocessors = catalogue.create('dataspec', 'preprocessor')


def lookup_type(key):
    return registry.types.get(key)
