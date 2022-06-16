import pytest

import datacraft
from . import builder


@pytest.fixture()
def spec_builder():
    return builder.spec_builder()


def test_uniform_distribution():
    dist_func = datacraft.registry.distribution.get('uniform')
    distribution = dist_func(start=5, end=10)

    values = set([int(distribution.next_value()) for _ in range(1000)])
    assert len(values) == 5


def test_normal_distribution():
    dist_func = datacraft.registry.distribution.get('normal')
    distribution = dist_func(mean=5, stddev=1)

    values = set([int(distribution.next_value()) for _ in range(1000)])
    assert 4 <= len(values) >= 5


def test_bounded_normal_distribution():
    dist_func = datacraft.registry.distribution.get('normal')
    distribution = dist_func(mean=5, stddev=1, min=2, max=7)

    values = set([int(distribution.next_value()) for _ in range(1000)])
    for value in values:
        assert 2 <= value <= 7


valid_funcs = [
    ('uniform(start=5, end=10)', 5),
    ('normal(mean=5, stddev=2)', 5),
    ('gauss(mean=5, stddev=2)', 5),
    ('gaussian(mean=5, stddev=2)', 5),
    ('gaussian(mean=5, stddev=2, min=3, max=9)', 5),
    ('gaussian(mean=33, stddev=5, max=50)', 10),
]


@pytest.mark.parametrize("string_func,min_values_generated", valid_funcs)
def test_from_string_normal(string_func, min_values_generated):
    distribution = datacraft.distributions.from_string(string_func)

    values = set([int(distribution.next_value()) for _ in range(100)])
    assert len(values) >= min_values_generated


invalid_funcs = [
    "normal(5, 2)",  # no names
    "noormal(mean=5, stddev=2)",  # invalid spelling of distribution
    "normal(means=5, stddev=2)",  # invalid spelling of param
    "",  # empty string not valid
    " ",  # white space not valid
    "()",  # open close parens not valid
    "normal()",  # no args
    "uniform(start=20, end=30",  # missing closing paren
    "uniform)start=20, end=30(",  # inverted parens
    "gauss(mean=33, stddev=5, maximum=50)"  # maximum is not a valid extra arg
    "gauss(mean=33, stddev=5, )"  # extra comma
]


@pytest.mark.parametrize("invalid_func_str", invalid_funcs)
def test_invalid_from_string(invalid_func_str):
    with pytest.raises(ValueError):
        dist = datacraft.distributions.from_string(invalid_func_str)
        dist.next_value()


valid_func_data = [
    'uniform(start=5, end=10)',
    'normal(mean=5, stddev=2)',
    'gauss(mean=5, stddev=2)',
    'gaussian(mean=5, stddev=2)',
    'gaussian(mean=5, stddev=2, min=3, max=9)',
    'gaussian(mean=33, stddev=5, max=50)',
]


@pytest.mark.parametrize("string_func", valid_func_data)
def test_distribution_type(string_func, spec_builder):
    spec_builder.distribution('dist', data=string_func)
    spec = spec_builder.build()

    val = next(spec.generator(1, enforce_schema=True))['dist']

    assert isinstance(val, float)


@pytest.mark.parametrize("invalid_func_str", invalid_funcs)
def test_invalid_distribution_spec(invalid_func_str, spec_builder):
    spec_builder.distribution('dist', data=invalid_func_str)
    spec = spec_builder.build()
    with pytest.raises(ValueError):
        next(spec.generator(1, enforce_schema=True))
