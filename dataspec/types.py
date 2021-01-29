import catalogue


class registry:
    types = catalogue.create('dataspec', 'type')
    preprocessors = catalogue.create('dataspec', 'preprocessor')
    logging = catalogue.create('dataspec', 'logging')


def lookup_type(key):
    return registry.types.get(key)
