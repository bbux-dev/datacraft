import json

import pytest

import datacraft
import datacraft._infer.default_analyzer as default_analyzer
import datacraft._infer.geo_analyzers as geo_alalyzers
import datacraft._infer.num_analyzers as num_analyzers
import datacraft._infer.str_analyzers as str_analyzers


@pytest.mark.parametrize(
    "values,compatible",
    [
        ([1], True),
        ([1, 2, 3], True),
        ([[1, 2], [3, 4, 5]], True),
        ([True], False),
        ([1, 0, False], False),
        ([[1, 2], ["a", "b", "c"]], False),
        ([[3, 2, 1], 1, 2], False)
    ]
)
def test_int_value_analyzer_is_compatible(values, compatible):
    analyzer = num_analyzers.IntValueAnalyzer()

    if compatible:
        assert analyzer.compatibility_score(values) > 0
    else:
        assert analyzer.compatibility_score(values) == 0


def test_int_value_analyzer_generate_spec():
    expected = {
        'type': 'rand_int_range',
        'data': [1, 10]
    }
    analyzer = num_analyzers.IntValueAnalyzer()
    values = list(range(1, 10 + 1))
    generated = analyzer.generate_spec("foo", values, None)
    assert generated == expected, f"Did not match. Generated: {json.dumps(generated)}, Expected: {json.dumps(expected)}"


# Tests for FloatValueAnalyzer
@pytest.mark.parametrize(
    "values,compatible",
    [
        ([1.1], True),
        ([1.1, 2.2, 3.3], True),
        ([[1.1, 2.2], [3.3, 4.4]], True),
        ([True], False),
        ([1, 0.0, False], False),
        ([[1.1, 2.2], ["a", "b"]], False),
        ([[1.1, 2.2], 1.3, 3.1], False)
    ]
)
def test_float_value_analyzer_is_compatible(values, compatible):
    analyzer = num_analyzers.FloatValueAnalyzer()

    if compatible:
        assert analyzer.compatibility_score(values) > 0
    else:
        assert analyzer.compatibility_score(values) == 0


def test_float_value_analyzer_generate_spec():
    expected = {
        'type': 'rand_range',
        'data': [1.1, 10.1]
    }
    analyzer = num_analyzers.FloatValueAnalyzer()
    values = [x + 0.1 for x in range(1, 11)]  # [1.1, 2.1, ... 10.1]
    generated = analyzer.generate_spec("foo", values, None)
    assert generated == expected, f"Did not match. Generated: {json.dumps(generated)}, Expected: {json.dumps(expected)}"


# Tests for StringValueAnalyzer
@pytest.mark.parametrize(
    "values,compatible",
    [
        (["a"], True),
        (["a", "b", "c"], True),
        ([["a", "b"], ["c", "d"]], True),
        ([True], False),
        (["a", "b", False], False),
        ([["a", "b"], [1, 2]], False)
    ]
)
def test_string_value_analyzer_is_compatible(values, compatible):
    analyzer = str_analyzers.StringValueAnalyzer()

    if compatible:
        assert analyzer.compatibility_score(values) > 0
    else:
        assert analyzer.compatibility_score(values) == 0


# Tests for StringValueAnalyzer
@pytest.mark.parametrize(
    "values,expected",
    [
        (["a"], {"type": "values", "data": ["a"]}),
        (["a", "b", "c"], {"type": "values", "data": ["a", "b", "c"]}),
        ([["a", "b"], ["c", "d"]],
         {
             "type": "values",
             "data": ["a", "b", "c", "d"],
             "config": {"count": {"2": 1.0}, "as_list": True}
         }),
        (["a", "a", "a", "b", "b", "c", "d", "e"],
         {
             "type": "values",
             "data": {
                 "a": 0.375,
                 "b": 0.25,
                 "c": 0.125,
                 "d": 0.125,
                 "e": 0.125
             }
         })
    ]
)
def test_string_value_analyzer_generate_spec(values, expected):
    analyzer = str_analyzers.StringValueAnalyzer()
    generated = analyzer.generate_spec("foo", values, None)
    assert generated == expected, f"Did not match. Generated:" \
                                  f" {json.dumps(generated)}, Expected:" \
                                  f" {json.dumps(expected)}"


# Tests for DefaultValueAnalyzer
@pytest.mark.parametrize(
    "values,expected",
    [
        # nested int lists
        ([[1, 2, 103]],
         {"type": "rand_int_range", "data": [1, 103], "config": {"count": {"3": 1.0}, "as_list": True}}),
        # nested str lists
        ([["do", "re", "me"], ["fa", "so"]],
         {"type": "values", "data": ["do", "fa", "me", "re", "so"],
          "config": {"count": {"3": 0.5, "2": 0.5}, "as_list": True}}),
        # mixed nested lists
        ([["do", "re", "me"], [1, 2, 3]],
         {"type": "values", "data": [["do", "re", "me"], [1, 2, 3]]}),
        # int lists
        ([1, 2, 103],
         {"type": "rand_int_range", "data": [1, 103]}),
        # requires substitution
        ([1, None, 103],
         {"type": "values", "data": [1, '_NONE_', 103]}),
        # unique strings
        (["foo", "bar", "baz"],
         {"type": "values", "data": ["foo", "bar", "baz"]}),
        # weighted values
        (["a", "a", "a", "b", "b", "c"],
         {"type": "values", "data": {"a": 0.5, "b": 0.33333, "c": 0.16667}}),

    ]
)
def test_default_analyzer(values, expected):
    analyzer = default_analyzer.DefaultValueAnalyzer()
    generated = analyzer.generate_spec("foo", values, None)
    assert generated == expected, f"Did not match. Generated:" \
                                  f" {json.dumps(generated)}, Expected:" \
                                  f" {json.dumps(expected)}"


def test_default_analyzer_sample_size():
    analyzer = default_analyzer.DefaultValueAnalyzer()
    values = ["a", "b", "c", "d", "e", "f"]
    generated = analyzer.generate_spec("foo", values, None, limit=3)
    assert len(generated['data']) == 3


def test_default_analyzer_limit_weighted():
    analyzer = default_analyzer.DefaultValueAnalyzer()
    values = ["a", "a", "a", "a", "b", "b", "b", "c", "c", "d", "e", "f"]
    generated = analyzer.generate_spec("foo", values, None, limit=3, limit_weighted=True)
    assert isinstance(generated['data'], dict)
    assert len(generated['data']) == 3


def test_default_analyzer_compatibility():
    # for coverage
    assert default_analyzer.DefaultValueAnalyzer().compatibility_score([1, 2, 3]) == 0.5


def test_geo_analyzer_lats():
    analyzer = geo_alalyzers.SimpleLatLongAnalyzer()
    lat_values = datacraft.values_for({"type": "geo.lat"}, 1000)
    assert analyzer.compatibility_score(v for v in lat_values) > 0
    spec = analyzer.generate_spec("lat", lat_values, None)
    assert spec == {"type": "geo.lat"}


def test_geo_analyzer_longs():
    analyzer = geo_alalyzers.SimpleLatLongAnalyzer()
    lat_values = datacraft.values_for({"type": "geo.long", "config": {"start_long": -180.0, "end_long": -90.0}}, 1000)
    assert analyzer.compatibility_score(v for v in lat_values) > 0
    spec = analyzer.generate_spec("long", lat_values, None)
    assert spec == {"type": "geo.long"}
