import pytest
from dataspec.loader import Loader
from dataspec import SpecException, suppliers
# to engage registration
from dataspec.type_handlers import select_list_subset


def test_invalid_when_no_config():
    _test_invalid_select_list_spec({"field:select_list_subset": {}})


def test_invalid_when_no_mean_specified():
    _test_invalid_select_list_spec({"field:select_list_subset?stddev=1": {}})


def test_invalid_when_ref_not_defined():
    spec = {
        "field:select_list_subset?mean=2": {
            "ref": "REF"
        }
    }
    _test_invalid_select_list_spec(spec)


def test_invalid_when_ref_and_data_specified():
    spec = {
        "field:select_list_subset?mean=2": {
            "ref": "REF",
            "data": ["one", "two", "three", "four"]
        }
    }
    _test_invalid_select_list_spec(spec)


def _test_invalid_select_list_spec(spec):
    with pytest.raises(SpecException):
        Loader(spec).get('field')


def test_select_list_basic():
    config = {
        'mean': 2,
        'stddev': 0,
        'join_with': '-'
    }
    supplier = suppliers.list_sampler(['a', 'b', 'c'], config)

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
    supplier = suppliers.list_sampler(['a', 'b', 'c'], config)

    # possible values are single element, all combos of two, and all combos of three
    possible = ['a', 'b', 'c',
                'a-b', 'a-c', 'b-a', 'b-c', 'c-a', 'c-b',
                'a-b-c', 'a-c-b', 'b-a-c', 'b-c-a', 'c-a-b', 'c-b-a']

    for i in range(0, 100):
        value = supplier.next(i)
        assert value in possible


def test_select_list_using_loader():
    spec = {"pets:select_list_subset?mean=2&stddev=0&join_with= ": ['dog', 'cat', 'pig', 'hog', 'bun']}
    loader = Loader(spec)
    supplier = loader.get('pets')
    value = supplier.next(0)
    assert len(value) == 7
