EXAMPLES = [
    ("overview_example_one", 7, """
refs = spec_builder.refs()
one = refs.values('ONE', ["A", "B", "C"])
two = refs.values('TWO', [1, 2, 3])

spec_builder.combine('combine', refs=[one, two])
""", ""),
    ("overview_example_two", 12, """
refs = spec_builder.refs()
one = refs.values('ONE', ["A", "B", "C"])
two = refs.values('TWO', [1, 2, 3, 4])

spec_builder.combine('combine', refs=[one, two])
""", "| sort"),
    ("overview_example_three", 5, """
refs = spec_builder.refs()
one = refs.values('ONE', ["A", "B", "C"], sample=True)
two = refs.values('TWO', [1, 2, 3, 4], sample="yes")

spec_builder.combine('combine', refs=[one, two])
""", ""),
    ("values_shorthand_one", 5, """
spec_builder.add_field('field1', dataspec.builder.values([1, 2, 3, 4, 5]))
spec_builder.add_field('field2', dataspec.builder.values({"A": 0.5, "B": 0.3, "C": 0.2}))
spec_builder.add_field('field3', dataspec.builder.values("CONSTANT"))
""", ""),
    ("values_shorthand_two", 5, """
spec_builder.add_field('field1', [1, 2, 3, 4, 5])
spec_builder.add_field('field2', {"A": 0.5, "B": 0.3, "C": 0.2})
spec_builder.add_field('field3', "CONSTANT")
""", ""),
    ("inline_key_example", 5, """
spec_builder.add_field("network:ipv4?cidr=192.168.0.0/16", {})
""", ""),
    ("config_example_one", 5, """
spec_builder.values('ONE', [1, 2, 3], prefix='TEST', suffix='@DEMO')
spec_builder.values('TWO?prefix=TEST&suffix=@DEMO', [1, 2, 3])
""", ""),
    ("common_config_example_one", 5, """
spec_builder.values('field', 
                    ["world", "beautiful", "destiny"], 
                    prefix='hello ')
""", ""),
    ("count_dist_example_one", 5, """
spec_builder.char_class(key='field',
                        data='visible',
                        count_dist='normal(mean=5, stddev=2, min=1, max=9)')
""", ""),
    ("constants_example_one", 5, """
spec_builder.values('constant1', 42)
spec_builder.add_field('shorthand_constant', "This is simulated data and should not be used for nefarious purposes")
""", ""),
    ("list_values_example_one", 5, """
spec_builder.values('list1', [200, 202, 303, 400, 404, 500])
spec_builder.add_field("shorthand_list",  [200, 202, 303, 400, 404, 500])
spec_builder.add_field("random_pet?sample=true", ["dog", "cat", "bunny", "pig", "rhino", "hedgehog"])
""", ""),
    ("weighted_values_example_one", 5, """
spec_builder.values('weighted1', {
    "200": 0.4, "202": 0.3, "303": 0.1,
    "400": 0.05, "403": 0.05, "404": 0.05, "500": 0.05
})
spec_builder.add_field("shorthand_weighted", {
    "200": 0.4, "202": 0.3, "303": 0.1,
    "400": 0.05, "403": 0.05, "404": 0.05, "500": 0.05
})
""", ""),
    ("sample_mode_example_one", 5, """
refs = spec_builder.refs()
refs.add_field('ONE?sample=true', ["A", "B", "C"])
refs.add_field('TWO?sample=true', [1, 2, 3, 4])

spec_builder.combine('combine', refs=['ONE', 'TWO'])
""", ""),
    ("combine_spec_example_one", 5, """
refs = spec_builder.refs()
first = refs.values(key="first",
                    data=["zebra", "hedgehog", "llama", "flamingo"])
last = refs.values(key="last",
                   data=["jones", "smith", "williams"])

spec_builder.combine('combine', refs=[first, last], join_with=" ")
""", ""),
    ("combine_list_spec_example_one", 5, """
refs = spec_builder.refs()
first = refs.values(
    key="first",
    data=["zebra", "hedgehog", "llama", "flamingo"])
last = refs.values(
    key="last",
    data=["jones", "smith", "williams"])
middle = refs.values(
    key="middle",
    data=["cloud", "sage", "river"])
middle_initial = refs.values(
    key="middle_initial",
    data={"a": 0.3, "m": 0.3, "j": 0.1, "l": 0.1, "e": 0.1, "w": 0.1})

spec_builder.combine_list(
    key='full_name',
    refs=[
        [first, last],
        [first, middle, last],
        [first, middle_initial, last],
        ],
    join_with=" ")
""", ""),
    ("uniform_date_example_exhaustive", 1000, """
spec_builder.add_field("dates:date?duration_days=90&start=15-Dec-2050 12:00&format=%d-%b-%Y %H:%M", {})
""", "\\\n  | sort -t- -k3n -k2n -k1n | uniq | sed -n '1p;$p'"),
    ("uniform_date_example_one", 5, """
spec_builder.add_field("dates:date", {})
""", "| sort -t- -k3n -k2n -k1n | uniq | sed -n '1p;$p'"),
    ("uniform_date_example_two", 5, """
spec_builder.add_field("dates:date?offset=1", {})
""", "| sort -t- -k3n -k2n -k1n | uniq | sed -n '1p;$p'"),
    ("uniform_date_example_three", 5, """
spec_builder.add_field("dates:date?duration_days=1", {})
""", "| sort -t- -k3n -k2n -k1n | uniq | sed -n '1p;$p'"),
    ("uniform_date_example_four", 5, """
spec_builder.add_field("dates:date?duration_days=10", {})
""", "| sort -t- -k3n -k2n -k1n | uniq | sed -n '1p;$p'"),
    ("uniform_date_example_five", 5, """
spec_builder.add_field("dates:date?duration_days=1&offset=1", {})
""", "| sort -t- -k3n -k2n -k1n | uniq | sed -n '1p;$p'"),
    ("uniform_date_example_six", 5, """
spec_builder.add_field("dates:date?duration_days=1&offset=-1", {})
""", "| sort -t- -k3n -k2n -k1n | uniq | sed -n '1p;$p'"),
    ("uniform_date_example_seven", 5, """
spec_builder.add_field("dates:date?duration_days=1&offset=1&start=15-12-2050", {})
""", "| sort -t- -k3n -k2n -k1n | uniq | sed -n '1p;$p'"),
    ("uniform_date_example_eight", 5, """
spec_builder.add_field("dates:date?duration_days=1&start=15-Dec-2050 12:00&format=%d-%b-%Y %H:%M", {})
""", "| sort -t- -k3n -k2M -k1n | uniq | sed -n '1p;$p'"),
    ("centered_date_example_exhaustive", 5, """
spec_builder.add_field("dates:date?center_date=20500601 12:00&format=%Y%m%d %H:%M&stddev_days=2", {})
""", "| sort -n | uniq | sed -n '1p;$p'"),
    ("centered_date_example_one", 5, """
spec_builder.add_field("dates:date?stddev_days=1", {})
""", "| sort -t- -k3n -k2n -k1n | uniq | sed -n '1p;$p'"),
    ("centered_date_example_two", 5, """
spec_builder.add_field("dates:date?stddev_days=15", {})
""", "| sort -t- -k3n -k2n -k1n | uniq | sed -n '1p;$p'"),
    ("range_spec_example_one", 5, """
spec_builder.range_spec(key="zero_to_ten", data=[0, 10, 0.5])
spec_builder.add_field(key="range_shorthand1:range", spec={"data": [0, 10, 0.5]})
spec_builder.add_field(key="range_shorthand2:range", spec=[0, 10, 0.5])
""", ""),
    ("range_spec_example_two", 5, """
spec_builder.range_spec(
    key="salaries",
    data=[
      [1000, 10000, 1000],
      [10000, 55000, 5000],
      [55000, 155000, 10000]
    ])
""", ""),
    ("rand_range_spec_example_one", 5, """
spec_builder.rand_range(
    key="population",
    data=[100, 1000],
    cast="int")
""", ""),
    ("uuid_spec_example_one", 5, """
spec_builder.uuid(key="id")
spec_builder.add_field("id_shorthand:uuid", {})
""", ""),
    ("char_class_spec_example_one", 5, """
spec_builder.add_field("one_to_five_digits:cc-digits?min=1&max=5", {})
""", ""),
    ("char_class_spec_example_two", 10, """
spec_builder.char_class(
    key="password",
    data=[
      "word",
      "special",
      "hex-lower",
      "M4$p3c!@l$@uc3"
    ],
    mean=14,
    stddev=2,
    min=10,
    max=18,
    exclude=["'", "\""])
""", ""),
    ("unicode_range_example_one", 10, """
spec_builder.unicode_range("text", ["3040", "309f"], mean=5)
""", ""),
    ("geo_point_spec_example_one", 5, """
    spec_builder.geo_pair("egypt", bbox=[31.33134, 22.03795, 34.19295, 25.00562], precision=3)
""", ""),
    ("ip_spec_example_one", 5, """
spec_builder.ipv4(key="network", cidr="2.22.222.0/16")
spec_builder.add_field("network_shorthand:ip?cidr=2.22.222.0/16", {})
spec_builder.add_field("network_with_base:ip?base=192.168.0", {})
""", ""),
    ("ip_precise_example_one", 5, """
spec_builder.add_field("network:ip.precise?cidr=10.0.0.0/8", {})
""", ""),
    ("ip_precise_example_two", 5, """
spec_builder.add_field("network:ip.precise?cidr=192.168.0.0/14&sample=true", {})
""", ""),
    ("ip_precise_example_three", 5, """
spec_builder.add_field("network:ip.precise?cidr=2.22.222.0/22", {})
""", ""),
    ("weighted_ref_example_one", 5, """
refs = spec_builder.refs()
refs.add_field('GOOD_CODES', {"200": 0.5, "202": 0.3, "203": 0.1, "300": 0.1})
refs.add_field('BAD_CODES', {"400": 0.5, "403": 0.3, "404": 0.1, "500": 0.1})

spec_builder.weightedref('http_code', data={"GOOD_CODES": 0.7, "BAD_CODES": 0.3})
""", ""),
    ("select_list_example_one", 5, """
spec_builder.select_list_subset(
    key="ingredients",
    data=["onions", "mushrooms", "garlic", "bell peppers", "spinach", "potatoes", "carrots"],
    mean=3,
    stddev=1,
    min=2,
    max=4,
    join_with=", ")
""", ""),
    ("select_list_example_two", 5, """
spec_builder.select_list_subset(
    key="ingredients",
    data=["onions", "mushrooms", "garlic", "bell peppers", "spinach", "potatoes", "carrots"],
    mean=3,
    stddev=1,
    min=2,
    max=4,
    join_with="\", \"",
    quote="\"")
""", ""),
    ("csv_spec_example_one", 5, """
spec_builder.csv(
    key="cities",
    datafile="cities.csv",
    delimiter="~",
    sample=True)
""", ""),
    ("csv_spec_example_two", 5, """
""", ""),
    ("csv_select_example_one", 5, """
""", ""),
    ("nested_example_one", 1, """
geo_fields = dataspec.spec_builder()
geo_fields.add_field("place_id:cc-digits?mean=5", {})
geo_fields.add_field("coordinates:geo.pair?as_list=true", {})

user_fields = dataspec.spec_builder()
user_fields.uuid("user_id")
user_fields.nested("geo", geo_fields.build())

spec_builder.uuid("id")
spec_builder.nested("user", user_fields.build())
""", ""),
]
