import os
from pathlib import Path
import datagen


def test_generator_string_template():
    names = ['bob', 'bobby', 'robert', 'bobo']
    spec =datagen. builder.single_field('name',datagen. builder.values(names)).build()

    template = 'Name: {{ name }}'
    processor = datagen.outputs.processor(template=template)

    gen = spec.generator(
        iterations=4,
        processor=processor)

    for name in names:
        assert next(gen) == f'Name: {name}'


def test_generator_path_template():
    spec = build_spec({'A': 1, 'B': 2, 'C': 3})

    dir_path = Path(os.path.dirname(os.path.realpath(__file__)))
    template = dir_path / 'data' / 'template.jinja'
    processor = datagen.outputs.processor(template=template)

    gen = spec.generator(
        iterations=1,
        processor=processor)

    rendered = next(gen)
    assert rendered == 'A:1, B:2, C:3'


def test_generator_no_template():
    names = ['bob', 'bobby', 'robert', 'bobo']
    spec =datagen. builder.single_field('name',datagen. builder.values(names)).build()

    gen = spec.generator(
        iterations=4,
        template=None)

    records = list(gen)
    assert len(records) == 4


def build_spec(data):
    spec_builder =datagen. builder.spec_builder()
    for key, value in data.items():
        spec_builder.add_field(key, value)
    return spec_builder.build()
