from typing import Any, Dict, Generator, List, Union, Callable
from collections import Counter

import datacraft
from datacraft import ValueListAnalyzer
from datacraft.suppliers import REPLACEMENTS

# using string keys, since 1, and 0 evaluate to True and False respectively
_LOOKUP = {
    "True": "_TRUE_",
    "False": "_FALSE_",
    "None": "_NONE_"
}


class IntValueAnalyzer(ValueListAnalyzer):
    def is_compatible(self, values: Generator[Any, None, None]) -> bool:
        return _simple_type_compatibility_check(values, int, _all_is_int)

    def generate_spec(self, values: List[Any]) -> Dict[str, Any]:
        return _generate_numeric_spec(values)


class FloatValueAnalyzer(ValueListAnalyzer):
    def is_compatible(self, values: Generator[Any, None, None]) -> bool:
        return _simple_type_compatibility_check(values, float, _all_is_float)

    def generate_spec(self, values: List[Any]) -> Dict[str, Any]:
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


class StringValueAnalyzer(ValueListAnalyzer):
    def is_compatible(self, values: Generator[Any, None, None]) -> bool:
        return _simple_type_compatibility_check(values, str, _all_is_str)

    def generate_spec(self, values: List[Any]) -> Dict[str, Any]:
        if _is_nested_lists(v for v in values):
            return _compute_str_list_spec(values)
        return {
            "type": "values",
            "data": list(set(values))
        }


def _simple_type_compatibility_check(values: Generator[Any, None, None],
                                     type_check: type,
                                     list_check_func: Callable):
    """Checks to see if the values are of uniform type. This includes lists of lists of the values.

    Args:
        values: generator for values to check
        type_check: type of values to expect
        list_check_func: function for testing lists of this type

    Returns:
        (bool): if the values are compatible with this type

    Examples
        >>> _simple_type_compatibility_check((v for v in [1, 2, 3]), int, _is_all_int)
        True
        >>> _simple_type_compatibility_check((v for v in [1, 'a', 3]), int, _is_all_int)
        False
        >>> _simple_type_compatibility_check((v for v in [[1], [2], [-3]), int, _is_all_int)
        True
        >>> _simple_type_compatibility_check((v for v in [[1, 2], 2, 3]), int, _is_all_int)
        False
    """
    value_type = None
    result = True
    # since generator check one value at a time until condition invalidated
    for value in values:
        if isinstance(value, list):
            if value_type is None:
                value_type = 'lists'
            elif value_type == str(type_check):
                result = False
                break
            if not list_check_func(value):
                result = False
                break
        elif not isinstance(value, type_check) or isinstance(value, bool):
            result = False
        else:
            if value_type is None:
                value_type = str(type_check)
            elif value_type == 'lists':
                result = False
                break
    return result


class DefaultValueAnalyzer(ValueListAnalyzer):
    """ when nothing else works """

    def is_compatible(self, values: Generator[Any, None, None]) -> bool:
        return True

    def generate_spec(self, values: List[Any]) -> Dict[str, Any]:
        # insert mechanism here to elegantly handle all the types of lists of values
        # handle leaf nodes that are lists
        if _is_nested_lists(v for v in values):
            if _all_is_numeric(values[0]):
                return _compute_list_range(values)
            if _all_list_is_str(values):
                return _compute_str_list_spec(values)
            return {
                "type": "values",
                "data": values
            }
        if len(set(values)) > 1 and _all_is_numeric(values):
            return _compute_range(values)
        if _requires_substitution(values):
            values = _substitute(values)

        # unique values, just rotate through them
        if _are_values_unique(values):
            return {
                "type": "values",
                "data": values
            }
        # use weighted values
        return {
            "type": "values",
            "data": _calculate_weights(values)
        }


@datacraft.registry.analyzers('default')
def _default_analyzer() -> datacraft.ValueListAnalyzer:
    return DefaultValueAnalyzer()


@datacraft.registry.analyzers('integer')
def _integer_analyzer() -> datacraft.ValueListAnalyzer:
    return IntValueAnalyzer()


@datacraft.registry.analyzers('float')
def _float_analyzer() -> datacraft.ValueListAnalyzer:
    return FloatValueAnalyzer()


@datacraft.registry.analyzers('string')
def _string_analyzer() -> datacraft.ValueListAnalyzer:
    return StringValueAnalyzer()


def _is_replacement(sublist):
    return any(v in REPLACEMENTS for v in sublist)


def _is_nested_lists(values: Generator[Any, None, None]):
    for item in values:
        if not isinstance(item, list):
            return False
    return True


def _requires_substitution(values: List[Any]):
    return _any_is_boolean(values) or _any_is_none(values)


def _substitute(values):
    return [_LOOKUP.get(str(v), v) for v in values]


def _all_is_numeric(values):
    return all((isinstance(value, (int, float)) and not isinstance(value, bool)) for value in values)


def _all_is_int(values):
    return all((isinstance(value, int) and not isinstance(value, bool)) for value in values)


def _all_is_float(values):
    return all((isinstance(value, float) and not isinstance(value, bool)) for value in values)


def _all_is_str(values):
    return all(isinstance(value, str) for value in values)


def _all_lists_numeric(values):
    return all(_all_is_numeric(sublist) for sublist in values)


def _all_is_of_type(values, type_check):
    return all(isinstance(val, type_check) for val in values)


def _all_lists_of_type(lists, type_check):
    return all(isinstance(val, type_check) for sublist in lists for val in sublist)


def _any_is_boolean(values):
    return any(isinstance(value, bool) for value in values)


def _any_is_none(values):
    return any(v is None for v in values)


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

    weights = _caclulate_list_size_weights(values)

    if _all_lists_of_type(values, int):
        field_type = "rand_int_range"
    else:
        field_type = "rand_range"

    return {
        "type": field_type,
        "data": [min_value, max_value],
        "config": {"count": weights, "as_list": True}
    }


def _caclulate_list_size_weights(values):
    # Calculate the frequency of each sublist length
    length_freq = Counter(len(sublist) for sublist in values)
    # Calculate the total number of lists
    total_lists = len(values)
    # Calculate the weights for each sublist length
    weights = {str(length): freq / total_lists for length, freq in length_freq.items()}
    return weights


def _compute_str_list_spec(values: list) -> dict:
    """
    Creates string spec from lists of list of strings
    Args:
        values: list of lists of strings

    Returns:
        (dict): with appropriate string spec
    """

    weights = _caclulate_list_size_weights(values)
    # Flatten the list of lists
    flat_list = [s for sublist in values for s in sublist]

    # Determine the number of unique strings
    unique_strings = set(flat_list)
    num_unique = len(unique_strings)

    # Determine the range of sizes of the strings
    sizes = [len(s) for s in unique_strings]
    min_size = min(sizes)
    max_size = max(sizes)
    avg_size = sum(sizes) / num_unique

    # Count occurrences of each string
    counts = Counter(flat_list)

    # Filter and count the strings that appear more than once
    repeated_count = sum(1 for count in counts.values() if count > 1)

    return {
        "type": "values",
        "data": flat_list,
        "config": {"count": weights, "as_list": True}
    }


def _calculate_weights(values: List[str]) -> Dict[str, float]:
    """
    Calculate the weights of occurrences of values from a list.

    Args:
        values (List[str]): A list of string values.

    Returns:
        Dict[str, float]: A dictionary containing each unique value from the list as the key
                          and its corresponding weight (or relative frequency) as the value.
    """
    total_count = len(values)
    counts = Counter(values)

    return {key: count / total_count for key, count in counts.items()}


def _are_values_unique(values: List) -> bool:
    """
    Check if all values in the list are unique.

    Args:
        values (List): A list of values.

    Returns:
        bool: True if all values are unique, otherwise False.
    """
    return len(values) == len(set(values))


def _all_list_is_str(lists):
    return all(isinstance(val, str) for sublist in lists for val in sublist)
