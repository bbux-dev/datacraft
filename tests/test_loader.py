from collections import Counter

import pytest

import datacraft
from datacraft import builder

spec = datacraft.builder.spec_builder() \
    .add_field('foo', builder.combine(['ONE', 'TWO'], join_with='')) \
    .add_ref('ONE', builder.values(['do', 'ca', 'pi'])) \
    .add_ref('TWO', builder.values(['g', 't', 'g'])) \
    .build()


def test_load_spec_invalid_key():
    loader = datacraft.field_loader(spec)
    with pytest.raises(datacraft.SpecException):
        loader.get('unknown')


def test_load_spec_missing_type_defaults_to_values():
    spec_missing_type = {
        'foo': {
            'data': ['one', 'two', 'tre']
        }
    }
    loader = datacraft.field_loader(spec_missing_type)
    supplier = loader.get('foo')

    assert supplier.next(0) == 'one'
    assert supplier.next(1) == 'two'
    assert supplier.next(2) == 'tre'


def test_load_spec_undefined_refs():
    spec_undefined_refs = builder.spec_builder() \
        .add_field('foo', builder.combine(['ONE', 'TWO'])) \
        .build()
    loader = datacraft.field_loader(spec_undefined_refs)
    with pytest.raises(datacraft.SpecException):
        loader.get('foo')


def test_load_spec_valid():
    loader = datacraft.field_loader(spec)
    supplier = loader.get('foo')

    assert supplier.next(0) == 'dog'
    assert supplier.next(1) == 'cat'
    assert supplier.next(2) == 'pig'


def test_load_spec_weighted_ref():
    ref_weights = {
        "POSITIVE": 0.5,
        "NEGATIVE": 0.4,
        "NEUTRAL": 0.1
    }
    weighted_ref = builder.spec_builder() \
        .add_field('foo', builder.weighted_ref(ref_weights)) \
        .add_ref('POSITIVE', ['yes']) \
        .add_ref('NEGATIVE', ['no']) \
        .add_ref('NEUTRAL', ['meh']) \
        .build()
    loader = datacraft.field_loader(weighted_ref)
    supplier = loader.get('foo')

    # expect mostly positive and negative values
    data = [supplier.next(i) for i in range(0, 100)]
    counter = Counter(data)
    # get the top two most common entries, which should be yes and no
    most_common_keys = [item[0] for item in counter.most_common(2)]

    assert 'yes' in most_common_keys
    assert 'no' in most_common_keys


def test_shortcut_notation_config_in_key():
    config_in_key_spec = {
        'foo?prefix=TEST': [1, 2, 3, 4, 5]
    }
    loader = datacraft.field_loader(config_in_key_spec)
    supplier = loader.get('foo')

    _verify_expected_values(supplier, 5, ['TEST1', 'TEST2', 'TEST3', 'TEST4', 'TEST5'])


def test_load_ref_by_name():
    refs_only_spec = builder.spec_builder() \
        .add_ref('ONE', 'uno') \
        .add_ref('TWO', 'dos') \
        .build()

    loader = datacraft.field_loader(refs_only_spec)
    assert loader.get('ONE').next(0) == 'uno'
    assert loader.get('TWO').next(0) == 'dos'


def test_registered_invalid_preprocessor():
    @datacraft.registry.preprocessors('test_invalid')
    def _do_stuff(_, __):
        return None

    raw_spec = {
        'foo': {'type': 'values', 'data': 42},
        # this one doesn't exist, so should get logged as such
        'bar': {'type': 'magical', 'data': 'fairy dust'}
    }
    # for coverage
    datacraft.loader.preprocess_spec(raw_spec)


def _verify_expected_values(supplier, iterations, expected_values):
    data = [supplier.next(i) for i in range(iterations)]
    assert data == expected_values
