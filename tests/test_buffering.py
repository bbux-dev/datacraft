import pytest

import datacraft

from . import builder


def test_buffered_supplier_one_behind():
    """
    Tests simple case that multiple calls to the same index will return the same result
    """
    wrapped = datacraft.suppliers.values(builder.values(['a', 'b', 'c', 'd', 'e', 'f', 'g'], sample=True))
    buffered = datacraft.supplier.common.BufferedValueSupplier(wrapped, buffer_size=3)

    for i in range(10):
        value = buffered.next(i)
        assert value == buffered.next(i)
        assert value == buffered.next(i)


def test_buffered_supplier_more_than_one_behind():
    """
    Tests that we will the buffered gets filled in an expected way
    """
    wrapped = datacraft.suppliers.values(builder.values(['a', 'b', 'c', 'd', 'e', 'f', 'g'], sample=True))
    buffered = datacraft.supplier.common.BufferedValueSupplier(wrapped, buffer_size=4)

    vals = [buffered.next(i) for i in range(5)]

    # buffer only holds 4 items so should only be able to reach back to third element
    assert buffered.next(4) == vals[-1]
    assert buffered.next(3) == vals[-2]
    assert buffered.next(2) == vals[-3]
    assert buffered.next(1) == vals[-4]

    with pytest.raises(ValueError):
        buffered.next(0)


def test_buffered_supplier_size_one():
    """
    Tests simple case but with a buffer of size one
    """
    wrapped = datacraft.suppliers.values(builder.values(['a', 'b', 'c', 'd', 'e', 'f', 'g'], sample=True))
    buffered = datacraft.supplier.common.BufferedValueSupplier(wrapped, buffer_size=1)

    for i in range(10):
        value = buffered.next(i)
        assert value == buffered.next(i)


def test_is_buffered():
    values_spec = builder.values(['a', 'b', 'c', 'd', 'e', 'f', 'g'], sample=True, buffer="on")
    assert datacraft.suppliers._is_buffered(**values_spec['config'])

    values_spec = builder.values(['a', 'b', 'c', 'd', 'e', 'f', 'g'], sample=True, buffer_size="20")
    assert datacraft.suppliers._is_buffered(**values_spec['config'])


def test_buffered_supplier_from_spec():
    """
    Tests interpreting specs for buffering
    """
    values_spec = builder.values(['a', 'b', 'c', 'd', 'e', 'f', 'g'], sample=True, buffer_size="20")
    assert datacraft.suppliers._is_buffered(**values_spec['config'])

    data_spec = builder.single_field('field', values_spec).build()
    loader = datacraft.loader.field_loader(data_spec)

    supplier = loader.get('field')

    for i in range(10):
        value = supplier.next(i)
        assert value == supplier.next(i)
