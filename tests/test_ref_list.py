from . import builder


def test_ref_list_all_refs():
    spec_builder = builder.spec_builder()
    spec_builder.add_ref('one', builder.values(1))
    spec_builder.add_ref('two', builder.values(2))
    spec_builder.ref_list('one_two', ref_names=['one', 'two'])
    generator = spec_builder.build().generator(1)
    assert next(generator) == {'one_two': [1, 2]}


def test_ref_list_refs_as_data():
    spec_builder = builder.spec_builder()
    spec_builder.add_ref('ehh', builder.values("a"))
    spec_builder.add_ref('bee', builder.values("b"))
    spec_builder.add_ref('see', builder.values("c"))
    spec_builder.ref_list('abc', data=['ehh', 'bee', 'see'])
    generator = spec_builder.build().generator(1)
    assert next(generator) == {'abc': ["a", "b", "c"]}
