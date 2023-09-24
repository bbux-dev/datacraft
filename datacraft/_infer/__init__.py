from typing import Any, Dict, Generator, List, Union
from collections import Counter

import datacraft
from datacraft import ValueListAnalyzer

_LOOKUP = {
    True: "_TRUE_",
    False: "_FALSE_",
    None: "_NONE_"
}


class IntValueAnalyzer(ValueListAnalyzer):
    def is_compatible(self, values: Generator[Any, None, None]) -> bool:
        """
        Check if all values are integers.

        Args:
            values (Generator[Any, None, None]): Generator producing values to check.

        Returns:
            bool: True if all values are integers, otherwise False.
        """
        for value in values:
            if not isinstance(value, int):
                return False
        return True

    def generate_spec(self, values: List[Any]) -> Dict[str, Any]:
        """
        Generate a specification for a list of integers.

        Args:
            values (List[Any]): List of integers to generate the spec for.

        Returns:
            Dict[str, Any]: Specification for the list of integers.
        """
        return {
            "type": "int",
            "min": min(values),
            "max": max(values)
        }


class FloatValueAnalyzer(ValueListAnalyzer):
    def is_compatible(self, values: Generator[Any, None, None]) -> bool:
        """
        Check if all values are floats.

        Args:
            values (Generator[Any, None, None]): Generator producing values to check.

        Returns:
            bool: True if all values are floats, otherwise False.
        """
        for value in values:
            if not isinstance(value, float):
                return False
        return True

    def generate_spec(self, values: List[Any]) -> Dict[str, Any]:
        """
        Generate a specification for a list of floats.

        Args:
            values (List[Any]): List of floats to generate the spec for.

        Returns:
            Dict[str, Any]: Specification for the list of floats.
        """
        return {
            "type": "float",
            "min": min(values),
            "max": max(values)
        }


class StringValueAnalyzer(ValueListAnalyzer):
    def is_compatible(self, values: Generator[Any, None, None]) -> bool:
        """
        Check if all values are strings.

        Args:
            values (Generator[Any, None, None]): Generator producing values to check.

        Returns:
            bool: True if all values are strings, otherwise False.
        """
        for value in values:
            if not isinstance(value, str):
                return False
        return True

    def generate_spec(self, values: List[Any]) -> Dict[str, Any]:
        """
        Generate a specification for a list of strings.

        Args:
            values (List[Any]): List of strings to generate the spec for.

        Returns:
            Dict[str, Any]: Specification for the list of strings.
        """
        return {
            "type": "string",
            "unique_strings": len(set(values))
        }


def compute_spec(values: List[Any], max_inspect_count: int = 100) -> Dict[str, Any]:
    """
    Compute the specification for a list of values.

    Args:
        values (List[Any]): List of values to compute the spec for.
        max_inspect_count (int, optional): Maximum number of values to inspect. Defaults to 100.

    Returns:
        Dict[str, Any]: Specification for the list of values.
    """
    analyzers = datacraft.registries.registered_analyzers()

    for analyzer in analyzers:
        if analyzer.is_compatible((v for i, v in enumerate(values) if i < max_inspect_count)):
            return analyzer.generate_spec(values)
    return {"type": "unknown"}


class DefaultValueAnalyzer(ValueListAnalyzer):
    """ when nothing else works """
    def is_compatible(self, values: Generator[Any, None, None]) -> bool:
        return True

    def generate_spec(self, values: List[Any]) -> Dict[str, Any]:
        # insert mechanism here to elegantly handle all the types of lists of values
        # handle leaf nodes that are lists
        if isinstance(values, list) and isinstance(values[0], list):
            if _is_numeric(values[0]):
                return _compute_list_range(values)
            if _all_list_is_str(values):
                return _compute_str_list_spec(values)
            return {
                "type": "values",
                "data": values
            }
        if len(set(values)) > 1 and _is_numeric(values):
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


def _requires_substitution(values):
    return _is_boolean(values) or _any_is_none(values)


def _substitute(values):
    return [_LOOKUP.get(v, v) for v in values]


def _is_numeric(values):
    return all((isinstance(value, (int, float)) and not isinstance(value, bool)) for value in values)


def _all_lists_numeric(values):
    return all(_is_numeric(sublist) for sublist in values)


def _all_lists_of_type(lists, type_check):
    return all(isinstance(val, type_check) for sublist in lists for val in sublist)


def _is_boolean(values):
    return all(isinstance(value, bool) for value in values)


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
    if not _is_numeric(values):
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
