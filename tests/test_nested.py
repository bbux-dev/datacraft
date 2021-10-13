import pytest
from datagen import builder, Loader
from datagen.supplier.core import nested


def test_single_nested():
    # Geo
    # - Place
    # - Coord
    geo_spec = builder.Builder() \
        .add_field("place_id:uuid", {}) \
        .add_field("coordinates", builder.geo_pair(as_list=True))
    spec = builder.Builder() \
        .add_field("id:uuid", {}) \
        .add_field("geo", builder.nested(fields=geo_spec.build())) \
        .build()
    supplier = Loader(spec).get('geo')

    first = supplier.next(0)
    assert isinstance(first, dict)
    assert list(first.keys()) == ['place_id', 'coordinates']


def test_multi_nested():
    # User
    # - Geo
    # - - Place
    # - - Coord
    geo_spec = builder.Builder() \
        .add_field("place_id:uuid", {}) \
        .add_field("coordinates", builder.geo_pair(as_list=True))
    user_spec = builder.Builder() \
        .add_field("user_id:uuid", {}) \
        .add_field("geo", builder.nested(fields=geo_spec.build()))
    spec = builder.Builder() \
        .add_field("id:uuid", {}) \
        .add_field("user", builder.nested(fields=user_spec.build())) \
        .build()
    supplier = Loader(spec).get('user')

    first = supplier.next(0)
    assert isinstance(first, dict)
    assert list(first.keys()) == ['user_id', 'geo']

    second = first['geo']
    assert isinstance(second, dict)
    assert list(second.keys()) == ['place_id', 'coordinates']


def test_single_nested_as_list():
    # Geo
    # - Place
    # - Coord
    geo_spec = builder.Builder() \
        .add_field("place_id:uuid", {}) \
        .add_field("coordinates", builder.geo_pair(as_list=True))
    spec = builder.Builder() \
        .add_field("id:uuid", {}) \
        .add_field("geo", builder.nested(fields=geo_spec.build(), as_list=True)) \
        .build()
    supplier = Loader(spec).get('geo')

    first = supplier.next(0)
    assert isinstance(first, list)
    assert list(first[0].keys()) == ['place_id', 'coordinates']


nested_count_examples = [
    (0, True, []),
    (0, False, None),
    (1, True, [{'inner': 'a'}]),
    (1, False, {'inner': 'a'}),
    (2, True, [{'inner': 'a'}, {'inner': 'b'}])
]


@pytest.mark.parametrize("count, as_list, expected", nested_count_examples)
def test_nested_count_edge_cases(count, as_list, expected):
    inner_spec = builder.spec_builder().values("inner", ["a", "b", "c"]).to_spec()
    spec = builder.spec_builder().nested("outer", inner_spec, count=count, as_list=as_list).to_spec()
    generator = spec.generator(1)
    single_record = next(generator)
    assert single_record['outer'] == expected
