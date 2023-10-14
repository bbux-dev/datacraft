import random
from typing import Any, Dict, List, Callable, Union
from typing import Generator

import datacraft
from datacraft import ValueListAnalyzer, RefsAggregator

from .helpers import (_simple_type_compatibility_check, _all_is_int, _all_is_float,
                      all_is_numeric, is_nested_lists, _all_lists_of_type,
                      calculate_list_size_weights)


class IntValueAnalyzer(ValueListAnalyzer):
    def compatibility_score(self, values: Generator[Any, None, None]) -> float:
        if _simple_type_compatibility_check(values, int, _all_is_int):
            return ValueListAnalyzer.MOSTLY_COMPATIBLE
        return ValueListAnalyzer.NOT_COMPATIBLE

    def generate_spec(self, name: str, values: List[Any], refs: RefsAggregator, **kwargs) -> Dict[str, Any]:
        return generate_numeric_spec(values, kwargs.get('limit', 0))


class FloatValueAnalyzer(ValueListAnalyzer):
    def compatibility_score(self, values: Generator[Any, None, None]) -> float:
        if _simple_type_compatibility_check(values, float, _all_is_float):
            return ValueListAnalyzer.MOSTLY_COMPATIBLE
        return ValueListAnalyzer.NOT_COMPATIBLE

    def generate_spec(self, name: str, values: List[Any], refs: RefsAggregator, **kwargs) -> Dict[str, Any]:
        return generate_numeric_spec(values, kwargs.get('limit', 0))


def generate_numeric_spec(values: List[Any], limit: int):
    if is_nested_lists(v for v in values):
        return compute_list_range(values)
    if len(set(values)) > 1 and all_is_numeric(values):
        return compute_range(values)

    if limit > 0 and len(values) > limit:
        values = random.sample(values, limit)
    return {
        "type": "values",
        "data": list(set(values))
    }


def compute_range(values: List[Union[int, float]]) -> Dict[str, Any]:
    """
    Compute the range from a list of numeric values.

    Args:
        values (List[Union[int, float]]): A list of numeric values.

    Returns:
        Dict[str, Any]: A dictionary with the structure:
            {
                "type": "rand_range",
                "data": [min, max]
            }
    """
    if not all_is_numeric(values):
        raise ValueError("All values in the list must be numeric.")

    type_key = "rand_range"
    if all(isinstance(value, int) for value in values):
        type_key = "rand_int_range"

    return {
        "type": type_key,
        "data": [min(values), max(values)]
    }


def compute_list_range(values: list) -> dict:
    """
    Creates rand_range spec for lists of values
    Args:
        values: list of lists of values

    Returns:
        (dict): rand_range or rand_int_range spec
    """
    max_value = max(num for sublist in values for num in sublist)
    min_value = min(num for sublist in values for num in sublist)

    weights = calculate_list_size_weights(values)

    if _all_lists_of_type(values, int):
        field_type = "rand_int_range"
    else:
        field_type = "rand_range"

    return {
        "type": field_type,
        "data": [min_value, max_value],
        "config": {"count": weights, "as_list": True}
    }


@datacraft.registry.analyzers('integer')
def _integer_analyzer() -> datacraft.ValueListAnalyzer:
    return IntValueAnalyzer()


@datacraft.registry.analyzers('float')
def _float_analyzer() -> datacraft.ValueListAnalyzer:
    return FloatValueAnalyzer()
