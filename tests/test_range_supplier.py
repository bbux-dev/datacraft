from datacraft import field_loader

from . import builder


def test_rand_range():
    spec = builder.spec_builder() \
        .add_field("field", builder.rand_range([100.9, 109.9], cast="int")) \
        .build()
    supplier = field_loader(spec).get('field')

    first = supplier.next(0)
    assert str(first).isnumeric()
    # occasionally gets rounded down to 100
    assert 100 <= first <= 110


def test_nested_range_lists_simple():
    data = [
        [0, 10],
        [20, 30]
    ]
    spec = builder.single_field("field:range", data).build()
    supplier = field_loader(spec).get('field')

    first = supplier.next(0)
    assert 0 <= first <= 10
    second = supplier.next(1)
    assert 20 <= second <= 30


def test_nested_range_lists_mixed_types_and_step():
    data = [
        [0, 10, 2],
        [20.0, 30.0]
    ]
    spec = builder.single_field("field:range", data).build()
    supplier = field_loader(spec).get('field')

    first = supplier.next(0)
    assert first % 2 == 0
    assert 0 <= first <= 10
    second = supplier.next(1)
    assert 20.0 <= second <= 30.0


def test_nested_range_lists_mixed_types_and_step_cast():
    data = [
        [0.5, 2.5, 0.5],
        [20.01234, 30.56789]
    ]
    spec = builder.single_field("field:range?cast=str&precision=2", data).build()
    supplier = field_loader(spec).get('field')

    assert supplier.next(0) == '0.5'
    assert supplier.next(1) == '20.01'


def test_range_wrap_around():
    data = [1, 3]
    spec = builder.single_field("field:range", data).build()
    supplier = field_loader(spec).get('field')

    vals = [supplier.next(i) for i in range(4)]
    assert vals == [1, 2, 3, 1]
