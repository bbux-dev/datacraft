import pytest
import dataspec.builder as builder


def test_api_builder():
    # raw data for both specs
    animal_names = ['zebra', 'hedgehog', 'llama', 'flamingo']
    action_list = ['fling', 'jump', 'launch', 'dispatch']
    domain_weights = {
        "gmail.com": 0.6,
        "yahoo.com": 0.3,
        "hotmail.com": 0.1
    }

    # first build uses **kwargs format
    builder1 = builder.Builder()
    builder1.add_refs(
        DOMAINS=builder.values(domain_weights),
        ANIMALS=builder.values(animal_names),
        ACTIONS=builder.values(action_list, sample=True),
        HANDLE=builder.combine(refs=['ANIMALS', 'ACTIONS'], join_with='_')  # combines ANIMALS and ACTIONS
    )
    builder1.add_fields(
        email=builder.combine(refs=['HANDLE', 'DOMAINS'])
    )

    spec1 = builder1.to_spec()

    # second builder uses the fluent api style
    builder2 = builder.Builder()

    animals_spec = builder.values(data=animal_names)
    actions_spec = builder.values(data=action_list, sample=True)
    domains_spec = builder.values(data=domain_weights)
    # combines ANIMALS and ACTIONS
    handle_spec = builder.combine(refs=['ANIMALS', 'ACTIONS'], join_with='_')

    builder2.add_ref('DOMAINS', domains_spec) \
        .add_ref('ANIMALS', animals_spec) \
        .add_ref('ACTIONS', actions_spec) \
        .add_ref('HANDLE', handle_spec)

    builder2.add_field('email', builder.combine(refs=['HANDLE', 'DOMAINS']))

    spec2 = builder2.to_spec()

    assert spec1 == spec2


valid_spec_build_tests = [
    (builder.values([1, 2, 3], prefix="foo"),
     {"type": "values", "data": [1, 2, 3], "config": {"prefix": "foo"}}),
    (builder.combine(refs=["ONE", "TWO"], join_with='@'),
     {"type": "combine", "refs": ["ONE", "TWO"], "config": {"join_with": "@"}}),
    (builder.combine(fields=["ONE", "TWO"], join_with='-'),
     {"type": "combine", "fields": ["ONE", "TWO"], "config": {"join_with": "-"}}),
    (builder.combine_list(refs=[["A", "B"], ["A", "B", "C"]], join_with=","),
     {"type": "combine-list", "config": {"join_with": ","}, "refs": [["A", "B"], ["A", "B", "C"]]}),
    (builder.range_spec(1, 5, 1, as_list=True, count=2),
     {"type": "range", "config": {"as_list": True, "count": 2}, "data": [1, 5, 1]}),
    (builder.rand_range(20, 44, count=[2, 3, 4]),
     {"type": "rand_range", "config": {"count": [2, 3, 4]}, "data": [20, 44]}),
    (builder.date(delta_days=3, offset=4),
     {"type": "date", "config": {"delta_days": 3, "offset": 4}}),
    (builder.date_iso(delta_days=4, offset=5),
     {"type": "date.iso", "config": {"delta_days": 4, "offset": 5}}),
    (builder.date_iso_us(delta_days=5, offset=6),
     {"type": "date.iso.us", "config": {"delta_days": 5, "offset": 6}}),
    (builder.uuid(quote="'"),
     {"type": "uuid", "config": {"quote": "'"}}),
    (builder.char_class("visible", min=5, max=7),
     {"type": "char_class", "config": {"min": 5, "max": 7}, "data": "visible"}),
    (builder.unicode_range(["3040", "309f"], mean=3),
     {"type": "unicode_range", "config": {"mean": 3}, "data": ["3040", "309f"]}),
    (builder.unicode_range([["3040", "309f"]], mean=3),
     {"type": "unicode_range", "config": {"mean": 3}, "data": [["3040", "309f"]]}),
    (builder.geo_lat(start_lat=75.5),
     {"type": "geo.lat", "config": {"start_lat": 75.5}}),
    (builder.geo_long(bbox=[31.3, 22.0, 34.1, 25.0]),
     {"type": "geo.long", "config": {"bbox": [31.3, 22.0, 34.1, 25.0]}}),
    (builder.geo_pair(join_with=":", as_list="yes"),
     {"type": "geo.pair", "config": {"join_with": ":", "as_list": "yes"}}),
    (builder.ip(base="192.168"),
     {"type": "ip", "config": {"base": "192.168"}}),
    (builder.ipv4(cidr="2.22.222.0/16"),
     {"type": "ipv4", "config": {"cidr": "2.22.222.0/16"}}),
    (builder.ip_precise(cidr="10.0.0.0/8"),
     {"type": "ip.precise", "config": {"cidr": "10.0.0.0/8"}}),
    (builder.weightedref({"One": 0.5, "Two": 0.3, "Three": 0.2}),
     {"type": "weightedref", "config": {}, "data": {"One": 0.5, "Two": 0.3, "Three": 0.2}}),
    (builder.select_list_subset(data=["A", "B", "C"], mean=5, stddev=2),
     {"type": "select_list_subset", "config": {"mean": 5, "stddev": 2}, "data": ["A", "B", "C"]}),
    (builder.select_list_subset(ref="LIST", mean=5, stddev=2),
     {"type": "select_list_subset", "config": {"mean": 5, "stddev": 2}, "ref": "LIST"}),
    (builder.csv(datafile="demo.csv", sample="on"),
     {"type": "csv", "config": {"datafile": "demo.csv", "sample": "on"}}),
    (builder.csv_select(data={"one": 1, "two": 2}, headers=False),
     {"type": "csv_select", "config": {"headers": False}, "data": {"one": 1, "two": 2}}),
    (builder.nested(fields={"one": {"type": "values", "data": 1}}),
     {"type": "nested", "config": {}, "fields": {"one": {"type": "values", "data": 1}}}),
]


@pytest.mark.parametrize("generated_spec,expected_spec", valid_spec_build_tests)
def test_spec_builder(generated_spec, expected_spec):
    assert generated_spec == expected_spec
