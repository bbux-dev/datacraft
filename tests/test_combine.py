import pytest

import datacraft.suppliers as suppliers
import datacraft
from . import builder


def test_neither_refs_nor_fields_specified():
    spec = _combine_spec_refs(["ONE", "TWO"])
    spec['field'].pop("refs")
    _test_invalid_combine_spec(spec)


def test_refs_specified_but_not_defined():
    spec = _combine_spec_refs(["ONE", "TWO"])
    spec['refs'].pop('ONE')
    spec['refs'].pop('TWO')
    _test_invalid_combine_spec(spec)


def test_refs_specified_but_not_all_defined():
    spec = _combine_spec_refs(["ONE", "TWO"])
    spec['refs'].pop('ONE')
    _test_invalid_combine_spec(spec)


def test_fields_specified_but_not_all_defined():
    spec = _combine_spec_fields(["one", "two"])
    spec.pop('one')
    _test_invalid_combine_spec(spec)


def test_combine_list_empty_refs_invalid():
    spec = _combine_list_spec([["ONE", "TWO"]])
    spec['refs'] = {}
    _test_invalid_combine_spec(spec)


def test_refs_specified_but_invalid_type():
    spec = _combine_list_spec([["ONE", "TWO"]])
    spec['refs']['TWO'] = builder.config_ref(prefix='foo', suffix='@bar')
    _test_invalid_combine_spec(spec)


def test_combine_list_no_refs():
    spec = {"field": {"type": "combine-list"}}
    _test_invalid_combine_spec(spec)


def test_combine_list_empty_refs():
    spec = {"field": {"type": "combine-list", "refs": []}}
    _test_invalid_combine_spec(spec)


def test_combine_list_refs_not_list_of_lists():
    spec = {"field": {"type": "combine-list", "refs": ["a", "b", "c"]}}
    _test_invalid_combine_spec(spec)


def _test_invalid_combine_spec(spec):
    with pytest.raises(datacraft.SpecException) as err:
        datacraft.loader.field_loader(spec).get('field')
    # for debugging
    # print(str(err.value))


def test_combine_lists():
    s1 = suppliers.values({'data': ['a', 'b', 'c']})
    s2 = suppliers.values({'data': [1, 2, 3, 4, 5]})
    s3 = suppliers.values({'data': ['foo', 'bar', 'baz', 'bin', 'oof']})

    combo = suppliers.combine([s1, s2, s3])

    assert combo.next(0) == 'a1foo'
    assert combo.next(1) == 'b2bar'
    assert combo.next(2) == 'c3baz'


def test_combine_fields():
    spec = builder.spec_builder() \
        .add_field("first", builder.values(["bob", "rob", "ann", "sue"])) \
        .add_field("last", builder.values(["smith", "jones", "frank", "wee"])) \
        .add_field("full_name", builder.combine(fields=["first", "last"], join_with=' ')) \
        .build()

    supplier = datacraft.loader.field_loader(spec).get('full_name')
    assert supplier.next(0) == 'bob smith'


def test_combine_list_spec_valid_but_weird1():
    spec = _combine_list_spec([["uno"]])
    supplier = datacraft.loader.field_loader(spec).get('field')
    assert supplier.next(0) == 'uno'
    assert supplier.next(1) == 'uno'


def test_combine_list_spec_valid_but_weird2():
    spec = _combine_list_spec([["uno", "dos"]])
    supplier = datacraft.loader.field_loader(spec).get('field')
    assert supplier.next(0) == 'unodos'
    assert supplier.next(1) == 'unodos'


def test_combine_list_spec_valid_normal():
    ref_lists = [
        ["ONE", "TWO"],
        ["TWO", "TRE"],
        ["TRE", "ONE"]
    ]
    spec = builder.spec_builder() \
        .add_field("field", builder.combine_list(refs=ref_lists)) \
        .add_ref("ONE", builder.values('uno')) \
        .add_ref("TWO", builder.values('dos')) \
        .add_ref("TRE", builder.values('tres')) \
        .build()

    supplier = datacraft.loader.field_loader(spec).get('field')
    assert supplier.next(0) == 'unodos'
    assert supplier.next(1) == 'dostres'
    assert supplier.next(2) == 'tresuno'


def test_combine_as_list():
    spec = _combine_spec_refs(["one", "two"], as_list=True)
    vals = list(spec.generator(1))
    assert vals[0] == {'field': ['one', 'two']}


def _combine_spec_refs(ref_names, **config):
    build = builder.spec_builder() \
        .add_field("field", builder.combine(refs=ref_names, **config))
    for name in ref_names:
        build.add_ref(name, builder.values(name))
    return build.build()


def _combine_spec_fields(field_names, **config):
    build = builder.spec_builder() \
        .add_field("field", builder.combine(fields=field_names, **config))
    for name in field_names:
        build.add_field(name, builder.values(name))
    return build.build()


def _combine_list_spec(ref_lists, **config):
    build = builder.spec_builder() \
        .add_field("field", builder.combine_list(refs=ref_lists, **config))
    for ref_list in ref_lists:
        for name in ref_list:
            build.add_ref(name, builder.values(name))
    return build.build()
