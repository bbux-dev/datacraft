from dataspec import builder, Loader
from dataspec.type_handlers import nested_handler


def test_single_nested():
    # Geo
    # - Place
    # - Coord
    geo_spec = builder.Builder() \
        .add_field("place_id:uuid", {}) \
        .add_field("coordinates", builder.geo_pair(as_list=True))
    spec = builder.Builder() \
        .add_field("id:uuid", {}) \
        .add_field("geo", builder.nested(fields=geo_spec.to_spec())) \
        .to_spec()
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
        .add_field("geo", builder.nested(fields=geo_spec.to_spec()))
    spec = builder.Builder() \
        .add_field("id:uuid", {}) \
        .add_field("user", builder.nested(fields=user_spec.to_spec())) \
        .to_spec()
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
        .add_field("geo", builder.nested(fields=geo_spec.to_spec(), as_list=True)) \
        .to_spec()
    supplier = Loader(spec).get('geo')

    first = supplier.next(0)
    assert isinstance(first, list)
    assert list(first[0].keys()) == ['place_id', 'coordinates']
