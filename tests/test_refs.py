import pytest
import datacraft
# to trigger registration
from datacraft import cli


def test_ref_with_ref_name():
    spec_builder = datacraft.spec_builder()
    spec_builder.add_ref('values', datacraft.builder.values([1, 2, 3]))
    spec_builder.ref('points_at_values', ref_name='values')
    generator = spec_builder.build().generator(1)
    assert next(generator) == {'points_at_values': 1}


def test_ref_with_data_as_name():
    spec_builder = datacraft.spec_builder()
    spec_builder.add_ref('values', datacraft.builder.values([1, 2, 3]))
    spec_builder.ref('points_at_values_with_prefix', data='values', prefix='@')
    generator = spec_builder.build().generator(1)
    assert next(generator) == {'points_at_values_with_prefix': '@1'}


def test_ref_missing_required():
    spec_builder = datacraft.spec_builder()
    spec_builder.add_ref('values', datacraft.builder.values([1, 2, 3]))
    spec_builder.ref('points_at_nothing')
    generator = spec_builder.build().generator(1)
    with pytest.raises(datacraft.SpecException):
        next(generator)


def test_config_ref_in_refs():
    spec_builder = datacraft.spec_builder()
    spec_builder.refs().config_ref('test', key1='value1', key2='value2')
    spec = spec_builder.build()
    assert 'refs' in spec
    assert spec['refs'].get('test') == {'type': 'config_ref', 'config': {'key1': 'value1', 'key2': 'value2'}}