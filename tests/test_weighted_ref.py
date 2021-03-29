import dataspec
import pytest


def test_weighted_ref_missing_key():
    spec = {
        'field': {
            'type': 'weightedref',
            'data': {
                'foo': 0.5,
                'bar': 0.4,
                'baz': 0.1,
            }
        },
        'refs': {
            'foo': ['foo'],
            'bar': 'bar',
            'baz': {'baz': 0.999}
        }
    }

    key_supplier = dataspec.suppliers.values(['foo', 'bar', 'baz', 'notvalid'])
    values_map = {key: dataspec.suppliers.values(value) for key, value in spec['refs'].items()}
    supplier = dataspec.suppliers.weighted_ref(key_supplier, values_map)

    with pytest.raises(dataspec.SpecException) as exception:
        [supplier.next(i) for i in range(0, 10)]
    assert "Unknown Key 'notvalid' for Weighted Reference" in str(exception.value)


def test_weighed_ref_count_as_list():
    spec = {
        'field': {
            'type': 'weightedref',
            'config': {'count': 3},
            'data': {
                'one': 0.5,
                'two': 0.4,
                'tre': 0.1,
            }
        },
        'refs': {
            'one': 'uno',
            'two': 'dos',
            'tre': 'tres'
        }
    }

    loader = dataspec.Loader(spec)
    supplier = loader.get('field')
    first = supplier.next(0)

    assert isinstance(first, list)
    assert len(first) == 3

