from dataspec import suppliers


def test_select_list_basic():
    config = {
        'mean': 2,
        'join_with': '-'
    }
    supplier = suppliers.select_list_subset(['a', 'b', 'c'], config)

    possible = ['a-b', 'a-c', 'b-a', 'b-c', 'c-a', 'c-b']

    for i in range(0, 6):
        value = supplier.next(i)
        assert value in possible


def test_select_list_mean_and_variance():
    config = {
        'mean': 2,
        'stddev': 1,
        'join_with': '-'
    }
    supplier = suppliers.select_list_subset(['a', 'b', 'c'], config)

    # possible values are single element, all combos of two, and all combos of three
    possible = ['a', 'b', 'c',
                'a-b', 'a-c', 'b-a', 'b-c', 'c-a', 'c-b',
                'a-b-c', 'a-c-b', 'b-a-c', 'b-c-a', 'c-a-b', 'c-b-a']

    for i in range(0, 100):
        value = supplier.next(i)
        assert value in possible
