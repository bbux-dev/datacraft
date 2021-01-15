import pytest

from dataspec import SpecException
from dataspec.type_handlers import range_handler


def test_ranges_missing_data():
    with pytest.raises(SpecException):
        range_handler.configure_supplier({'type': 'range'}, None)


def test_ranges_invalid_data_type():
    with pytest.raises(SpecException):
        range_handler.configure_supplier({'type': 'range', 'data': 42}, None)


def test_ranges_end_before_start():
    start = 10
    end = 9
    with pytest.raises(SpecException):
        range_handler.configure_supplier({'type': 'range', 'data': [start, end]}, None)


def test_ranges_valid():
    start = 2
    end = 10
    step = 2
    supplier = range_handler.configure_supplier({'type': 'range', 'data': [start, end, step]}, None)

    expected = [2, 4, 6, 8, 10]
    actual = [supplier.next(i) for i in range(5)]

    assert expected == actual


def test_ranges_float_step():
    start = 0
    end = 1
    step = .1
    supplier = range_handler.configure_supplier({'type': 'range', 'data': [start, end, step]}, None)

    expected = [0, .1, .2, .3, .4, .5, .6, .7, .8, .9, 1]
    actual = [supplier.next(i) for i in range(11)]

    assert expected == actual


def test_ranges_float_start_end():
    start = 0.5
    end = 5.5
    supplier = range_handler.configure_supplier({'type': 'range', 'data': [start, end]}, None)

    expected = [0.5, 1.5, 2.5, 3.5, 4.5, 5.5]
    actual = [supplier.next(i) for i in range(6)]

    assert expected == actual
