from typing import Any, Dict, List, Callable, Union
from typing import Generator

import datacraft
from datacraft import ValueListAnalyzer, RefsAggregator

from .helpers import (_simple_type_compatibility_check, _all_is_int, _all_is_float,
                      _all_is_numeric, _is_nested_lists, _all_lists_of_type,
                      _calculate_list_size_weights)


class IntValueAnalyzer(ValueListAnalyzer):
    def compatibility_score(self, values: Generator[Any, None, None]) -> float:
        if _simple_type_compatibility_check(values, int, _all_is_int):
            return ValueListAnalyzer.MOSTLY_COMPATIBLE
        return ValueListAnalyzer.NOT_COMPATIBLE

    def generate_spec(self, values: List[Any], refs: RefsAggregator) -> Dict[str, Any]:
        return _generate_numeric_spec(values)


class FloatValueAnalyzer(ValueListAnalyzer):
    def compatibility_score(self, values: Generator[Any, None, None]) -> float:
        if _simple_type_compatibility_check(values, float, _all_is_float):
            return ValueListAnalyzer.MOSTLY_COMPATIBLE
        return ValueListAnalyzer.NOT_COMPATIBLE

    def generate_spec(self, values: List[Any], refs: RefsAggregator) -> Dict[str, Any]:
        return _generate_numeric_spec(values)


def _generate_numeric_spec(values: List[Any]):
    if _is_nested_lists(v for v in values):
        return _compute_list_range(values)
    if len(set(values)) > 1 and _all_is_numeric(values):
        return _compute_range(values)
    return {
        "type": "values",
        "data": list(set(values))
    }


def _compute_range(values: List[Union[int, float]]) -> Dict[str, Any]:
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
    if not _all_is_numeric(values):
        raise ValueError("All values in the list must be numeric.")

    type_key = "rand_range"
    if all(isinstance(value, int) for value in values):
        type_key = "rand_int_range"

    return {
        "type": type_key,
        "data": [min(values), max(values)]
    }


def _compute_list_range(values: list) -> dict:
    """
    Creates rand_range spec for lists of values
    Args:
        values: list of lists of values

    Returns:
        (dict): rand_range or rand_int_range spec
    """
    max_value = max(num for sublist in values for num in sublist)
    min_value = min(num for sublist in values for num in sublist)

    weights = _calculate_list_size_weights(values)

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
