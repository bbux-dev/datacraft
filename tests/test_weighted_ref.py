# to trigger registration
import pytest

from datagen import builder, suppliers, Loader, SupplierException
from datagen.supplier.refs import weighted_ref_supplier
# to trigger registration
from datagen import cli


def test_weighted_ref_missing_key():
    ref_weights = {
        'foo': 0.5,
        'bar': 0.4,
        'baz': 0.1,
    }
    spec = builder.single_field('field', builder.weighted_ref(ref_weights)) \
        .add_ref('foo', ['foo']) \
        .add_ref('bar', 'bar') \
        .add_ref('baz', {'baz': 0.999}) \
        .build()

    key_supplier = suppliers.values(['foo', 'bar', 'baz', 'notvalid'])
    values_map = {key: suppliers.values(value) for key, value in spec['refs'].items()}
    supplier = weighted_ref_supplier(key_supplier, values_map)

    with pytest.raises(SupplierException) as exception:
        [supplier.next(i) for i in range(0, 10)]
    assert "Unknown Key 'notvalid' for Weighted Reference" in str(exception.value)


def test_weighed_ref_count_as_list():
    ref_weights = {
        'one': 0.5,
        'two': 0.4,
        'tre': 0.1,
    }
    spec = builder.single_field('field', builder.weighted_ref(ref_weights, count=3)) \
        .add_ref('one', 'uno') \
        .add_ref('two', 'dos') \
        .add_ref('tre', 'tres') \
        .build()

    loader = Loader(spec)
    supplier = loader.get('field')
    first = supplier.next(0)

    assert isinstance(first, list)
    assert len(first) == 3
