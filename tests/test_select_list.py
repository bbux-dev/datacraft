import pytest

import datacraft

from . import builder


def test_invalid_when_no_config():
    _test_invalid_select_list_spec({"field:sample": {}})


def test_invalid_when_no_mean_specified():
    _test_invalid_select_list_spec({"field:sample?stddev=1": {}})


def test_invalid_when_ref_not_defined():
    spec = builder.single_field("field:sample?mean=2", {"ref": "REF"}).build()
    _test_invalid_select_list_spec(spec)


def test_invalid_when_ref_and_data_specified():
    spec = builder.single_field("field?mean=2",
                                builder.select_list_subset(data=["one", "two", "three", "four"], ref="REF")).build()
    _test_invalid_select_list_spec(spec)


def _test_invalid_select_list_spec(spec):
    with pytest.raises(datacraft.SpecException):
        datacraft.loader.field_loader(spec).get('field')


def test_select_list_basic():
    config = {
        'mean': 2,
        'stddev': 0,
        'join_with': '-'
    }
    supplier = datacraft.suppliers.list_stats_sampler(['a', 'b', 'c'], **config)

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
    supplier = datacraft.suppliers.list_stats_sampler(['a', 'b', 'c'], **config)

    # possible values are single element, all combos of two, and all combos of three
    possible = ['a', 'b', 'c',
                'a-b', 'a-c', 'b-a', 'b-c', 'c-a', 'c-b',
                'a-b-c', 'a-c-b', 'b-a-c', 'b-c-a', 'c-a-b', 'c-b-a']

    for i in range(0, 100):
        value = supplier.next(i)
        assert value in possible


def test_select_list_using_loader():
    spec = {"pets:sample?mean=2&stddev=0&join_with= ": ['dog', 'cat', 'pig', 'hog', 'bun']}
    loader = datacraft.loader.field_loader(spec)
    supplier = loader.get('pets')
    value = supplier.next(0)
    assert len(value) == 7


def test_select_list_ref_contains_data():
    spec_builder = builder.spec_builder()
    spec_builder.select_list_subset('pets', data=None, ref_name='pets_list', count=2)
    spec_builder.refs().values(key='pets_list', data=['goat', 'sheep', 'bear', 'cow', 'dragon'])
    loader = datacraft.loader.field_loader(spec_builder.build())
    supplier = loader.get('pets')
    value = supplier.next(0)
    assert isinstance(value, list)
    assert len(value) == 2
