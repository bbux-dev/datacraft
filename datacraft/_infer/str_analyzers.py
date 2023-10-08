import random
import re
from collections import Counter
from typing import Any, Dict, List, Tuple
from typing import Generator, Union

import datacraft
from datacraft import ValueListAnalyzer, RefsAggregator
from .helpers import (_simple_type_compatibility_check, _all_is_str, _is_nested_lists,
                      _calculate_list_size_weights)

# UUID regex patterns
UUID_PATTERN = re.compile(r"^[A-Fa-f\d]{8}-[A-Fa-f\d]{4}-[A-Fa-f\d]{4}-[A-Fa-f\d]{4}-[A-Fa-f\d]{12}$")
UUID_PATTERN_LOWER = re.compile(r"^[a-f\d]{8}-[a-f\d]{4}-[a-f\d]{4}-[a-f\d]{4}-[a-f\d]{12}$")
UUID_PATTERN_UPPER = re.compile(r"^[A-F\d]{8}-[A-F\d]{4}-[A-F\d]{4}-[A-F\d]{4}-[A-F\d]{12}$")


class StringValueAnalyzer(ValueListAnalyzer):
    def compatibility_score(self, values: Generator[Any, None, None]) -> float:
        if _simple_type_compatibility_check(values, str, _all_is_str):
            # lots of types of strings, this is a default matcher, when others don't
            return ValueListAnalyzer.SOMEWHAT_COMPATIBLE + .01
        return ValueListAnalyzer.NOT_COMPATIBLE

    def generate_spec(self, name: str, values: List[Any], refs: RefsAggregator, **kwargs) -> Dict[str, Any]:
        if _is_nested_lists(v for v in values):
            return _compute_str_list_spec(values)
        sample_size = kwargs.get('sample_size', 0)
        if sample_size > 0:
            values = random.sample(values, sample_size)
        return {
            "type": "values",
            "data": list(set(values))
        }


class UuidValueAnalyzer(ValueListAnalyzer):
    def compatibility_score(self, values: Generator[Any, None, None]) -> float:
        if all_uuids(values):
            return ValueListAnalyzer.TOTALLY_COMPATIBLE
        return ValueListAnalyzer.NOT_COMPATIBLE

    def generate_spec(self, name: str, values: List[Any], refs: RefsAggregator, **kwargs) -> Dict[str, Any]:
        counts = count_uuid_cases(values)
        # this is a regular UUID
        if counts["lower"] > 0:
            return {
                "type": "uuid"
            }
        else:
            return {
                "type": "uuid",
                "config": {
                    "cast": "upper"
                }
            }


def all_uuids(gen: Generator[Union[str, int, float, bool], None, None]) -> bool:
    """
    Check if all values from a generator match a UUID pattern.

    The function will return False as soon as:
    - a value is not a string
    - a string value does not match the UUID pattern.

    Args:
        gen (Generator[Union[str, int, float, bool], None, None]): A generator of values.

    Returns:
        bool: True if all values match the UUID pattern, False otherwise.

    Examples:
        >>> g = (str(i) for i in ["e6e08c98-ae5b-4cc6-8866-0787596c2b4c", "4B8C6898-1F11-4E06-BB6C-5A52BFDECC18"])
        >>> all_uuids(g)
        True

        >>> g = (str(i) for i in ["e6e08c98-ae5b-4cc6-8866-0787596c2b4c", "invalid"])
        >>> all_uuids(g)
        False
    """
    for value in gen:
        if not isinstance(value, str) or UUID_PATTERN.match(value) is None:
            return False
    return True


def count_uuid_cases(uuids: List[str]) -> Dict[str, Any]:
    """
    Count the proportion of UUIDs in a list that are entirely in lowercase and uppercase.

    Args:
        uuids (List[str]): A list of UUID strings.

    Returns:
        Tuple[float, float]: A tuple containing two floats:
                             1. The proportion of lowercase UUIDs.
                             2. The proportion of uppercase UUIDs.

    Examples:
        >>> count_uuid_cases(["e6e08c98-ae5b-4cc6-8866-0787596c2b4c", "4B8C6898-1F11-4E06-BB6C-5A52BFDECC18"])
        (0.5, 0.5)
    """
    lower_count = sum(1 for uuid in uuids if UUID_PATTERN_LOWER.match(uuid))
    upper_count = sum(1 for uuid in uuids if UUID_PATTERN_UPPER.match(uuid))

    return {
        "lower": lower_count,
        "upper": upper_count
    }


def _compute_str_list_spec(values: list) -> dict:
    """
    Creates string spec from lists of list of strings
    Args:
        values: list of lists of strings

    Returns:
        (dict): with appropriate string spec
    """

    weights = _calculate_list_size_weights(values)
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


@datacraft.registry.analyzers('string')
def _string_analyzer() -> datacraft.ValueListAnalyzer:
    return StringValueAnalyzer()


@datacraft.registry.analyzers('uuid')
def _uuid_analyzer() -> datacraft.ValueListAnalyzer:
    return UuidValueAnalyzer()
