import pytest

import datacraft

cut_test_cases = [
    ("1234567890", 0, 1, "1"),
    ("1234567890", 0, 2, "12"),
    ("1234567890", 2, 4, "34"),
    ("1234567890", 9, 10, "0"),
    ("1234567890", 10, 12, ""),
    ("1234567890", 11, 12, ""),
]


@pytest.mark.parametrize('in_str,start,end,expected', cut_test_cases)
def test_cut(in_str, start, end, expected):
    wrapped = datacraft.suppliers.constant(in_str)
    cut = datacraft.suppliers.cut(wrapped, start, end)
    assert cut.next(0) == expected
