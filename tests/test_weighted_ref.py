import dataspec.suppliers as suppliers
from dataspec import SpecException
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

    key_supplier = suppliers.values(['foo', 'bar', 'baz', 'notvalid'])
    values_map = {key: suppliers.values(value) for key, value in spec['refs'].items()}
    supplier = suppliers.weighted_ref(key_supplier, values_map)

    with pytest.raises(SpecException) as exception:
        [supplier.next(i) for i in range(0, 10)]
    assert "Unknown Key 'notvalid' for Weighted Reference" in str(exception.value)
