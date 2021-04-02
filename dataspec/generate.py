"""
Module that handles generating records from the provided Data Spec
"""
from typing import Dict, Union
from pathlib import Path
from dataspec import key_providers, template_engines, Loader
# this activates the decorators, so they will be discoverable
from dataspec.type_handlers import *
from .preprocessor import *


def record_generator(spec: Dict, iterations: int, template: Union[str, Path] = None, data_dir='.', enforce_schema=False):
    """
    Creates a record_generator that will produce records or render the template for each record

    Usage:

    import dataspec
    from dataspec import builder

    spec = builder.single_field('name', builder.values(['bob', 'bobby', 'robert', 'bobo'])).build()

    template = 'Name: {{ name }}'

    record_generator = dataspec.record_generator(
        spec=spec,
        iterations=4,
        template=template)

    for i in range(5):
        try:
            record = next(record_generator)
            print(record)
        except StopIteration:
            pass

    :param spec: The Data Spec to use
    :param iterations: the number of iterations to run
    :param template: to apply to the data, string or Path
    :param data_dir: directory that contains data, if needed
    :param enforce_schema: if the schemas for each type should be checked
    :return: None
    """
    loader = Loader(spec, datadir=data_dir, enforce_schema=enforce_schema)

    if template is not None:
        if isinstance(template, Path):
            engine = template_engines.for_file(template)
        else:
            engine = template_engines.string(template)

    key_provider = key_providers.from_spec(loader.specs)

    for i in range(0, iterations):
        group, keys = key_provider.get()
        record = {}
        for key in keys:
            value = loader.get(key).next(i)
            record[key] = value
        if template is not None:
            yield engine.process(record)
        else:
            yield record
