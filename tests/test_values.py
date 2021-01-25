import dataspec.suppliers as suppliers
from dataspec.loader import _preprocess_spec
from dataspec.exceptions import SpecException
from collections import Counter
import pytest


def test_single_value():
    supplier = suppliers.values({'type': 'values', 'data': 42})

    data = [supplier.next(i) for i in range(0, 10)]

    counter = Counter(data)

    most_common_keys = [item[0] for item in counter.most_common(2)]

    assert len(most_common_keys) == 1
    assert 42 in most_common_keys


def test_values_list():
    supplier = suppliers.values({'data': [1, 2, 3, 4, 5]})

    data = [supplier.next(i) for i in range(0, 10)]

    counter = Counter(data)

    most_common_keys = [item[0] for item in counter.most_common(10)]

    assert len(most_common_keys) == 5
    assert [1, 2, 3, 4, 5] == most_common_keys


def test_weighted_values():
    supplier = suppliers.values({'data': {'foo': 0.5, 'bar': 0.4, 'baz': 0.1}})

    data = [supplier.next(i) for i in range(0, 100)]

    counter = Counter(data)

    most_common_keys = [item[0] for item in counter.most_common(2)]

    assert 'foo' in most_common_keys
    assert 'bar' in most_common_keys


def test_shortcut_notation():
    # not type or data key, just what would have been the value for the data key
    supplier = suppliers.values({'foo': 0.5, 'bar': 0.4, 'baz': 0.1})

    data = [supplier.next(i) for i in range(0, 100)]

    counter = Counter(data)

    most_common_keys = [item[0] for item in counter.most_common(2)]

    assert 'foo' in most_common_keys
    assert 'bar' in most_common_keys


def test_sampling_mode_invalid_for_weighted_values():
    spec = {
        'foo?sample=True': {10: 0.5, 20: 0.3, 30: 0.2}
    }
    updated = _preprocess_spec(spec)
    with pytest.raises(SpecException):
        suppliers.values(updated['foo'])
