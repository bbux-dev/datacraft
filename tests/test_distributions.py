import pytest
import dataspec
from dataspec import distributions


def test_uniform_distribution():
    dist_func = dataspec.registry.distribution.get('uniform')
    distribution = dist_func(start=5, end=10)

    values = set([int(distribution.next_value()) for _ in range(100)])
    assert len(values) == 5


def test_normal_distribution():
    dist_func = dataspec.registry.distribution.get('normal')
    distribution = dist_func(mean=5, stddev=1)

    values = set([int(distribution.next_value()) for _ in range(100)])
    assert len(values) >= 5


valid_funcs = [
    ('uniform(start=5, end=10)', 5),
    ('normal(mean=5, stddev=2)', 5),
    ('gauss(mean=5, stddev=2)', 5),
    ('gaussian(mean=5, stddev=2)', 5),
]


@pytest.mark.parametrize("string_func,min_values_generated", valid_funcs)
def test_from_string_normal(string_func, min_values_generated):
    distribution = dataspec.distributions.from_string(string_func)

    values = set([int(distribution.next_value()) for _ in range(100)])
    assert len(values) >= min_values_generated


invalid_funcs = [
    "normal(5, 2)",
    "noormal(mean=5, stddev=2)",
    "normal(means=5, stddev=2)",
    "",
    " ",
    "()",
    "normal()",
    "uniform(start=20, end=30",
    "uniform)start=20, end=30("
]


@pytest.mark.parametrize("invalid_func_str", invalid_funcs)
def test_invalid_from_string(invalid_func_str):
    with pytest.raises(ValueError):
        dist = dataspec.distributions.from_string(invalid_func_str)
        dist.next_value()
