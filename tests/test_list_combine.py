import dataspec.suppliers as suppliers


def test_combine_lists():
    s1 = suppliers.values({'data': ['a', 'b', 'c']})
    s2 = suppliers.values({'data': [1, 2, 3, 4, 5]})
    s3 = suppliers.values({'data': ['foo', 'bar', 'baz', 'bin', 'oof']})

    combo = suppliers.combine([s1, s2, s3], config={'join_with': ''})

    assert combo.next(0) == 'a1foo'
    assert combo.next(1) == 'b2bar'
    assert combo.next(2) == 'c3baz'
