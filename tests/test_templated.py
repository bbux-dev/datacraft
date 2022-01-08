import datacraft


def test_basic_template():
    supplier_map = {
        'chars': datacraft.suppliers.values(['a', 'b', 'c', 'd']),
        'nums': datacraft.suppliers.values([1, 2, 3, 4])
    }
    template_str = 'prefix {{ chars }} joins with {{ nums }} suffix'
    supplier = datacraft.suppliers.templated(supplier_map, template_str)

    assert supplier.next(0) == 'prefix a joins with 1 suffix'


def test_spec_based_templated():
    raw = {
        "field": {
            "type": "templated",
            "data": "system {{ char }}.{{ num }}",
            "refs": ["char", "num"]
        },
        "refs": {
            "char": ["a", "b", "c"],
            "num": [1, 2, 3]
        }
    }
    spec = datacraft.parse_spec(raw)
    single = list(spec.generator(1))
    assert single == [{'field': 'system a.1'}]


def test_builder_based_templated():
    builder = datacraft.spec_builder()
    builder.refs().values(key='health', data=[20, 25, 30])
    builder.refs().values(key='dex', data=[15, 16, 17])
    builder.templated(
        key='field',
        data='Health: {{ health }}, Dexterity: {{ dex }}',
        refs=['health', 'dex']
    )
    spec = builder.build()
    single = list(spec.generator(1))
    assert single == [{'field': 'Health: 20, Dexterity: 15'}]
