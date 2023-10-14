import random
import re
from collections import Counter
from typing import Any, Dict, List, Tuple
from typing import Generator, Union

import datacraft
from datacraft import ValueListAnalyzer, RefsAggregator
from .helpers import (_simple_type_compatibility_check, _all_is_str, is_nested_lists,
                      calculate_list_size_weights, calculate_weights, top_n_items,
                      is_significantly_duplicated, all_match_pattern)
from .num_analyzers import generate_numeric_spec

# UUID regex patterns
UUID_PATTERN = re.compile(r"^[A-Fa-f\d]{8}-[A-Fa-f\d]{4}-[A-Fa-f\d]{4}-[A-Fa-f\d]{4}-[A-Fa-f\d]{12}$")
UUID_PATTERN_LOWER = re.compile(r"^[a-f\d]{8}-[a-f\d]{4}-[a-f\d]{4}-[a-f\d]{4}-[a-f\d]{12}$")
UUID_PATTERN_UPPER = re.compile(r"^[A-F\d]{8}-[A-F\d]{4}-[A-F\d]{4}-[A-F\d]{4}-[A-F\d]{12}$")
INT_STRING_PATTERN = re.compile(r"^\d+$")


class StringValueAnalyzer(ValueListAnalyzer):
    def compatibility_score(self, values: Generator[Any, None, None]) -> float:
        if _simple_type_compatibility_check(values, str, _all_is_str):
            # lots of types of strings, this is a default matcher, when others don't
            return ValueListAnalyzer.SOMEWHAT_COMPATIBLE + .01
        return ValueListAnalyzer.NOT_COMPATIBLE

    def generate_spec(self, name: str, values: List[Any], refs: RefsAggregator, **kwargs) -> Dict[str, Any]:
        if is_nested_lists(v for v in values):
            return compute_str_list_spec(values)

        limit = kwargs.get('limit', 0)
        sample_weights = kwargs.get('limit_weighted', False)
        duplication_threshold = kwargs.get('duplication_threshold', 0.2)

        # unique values, just rotate through them
        if not is_significantly_duplicated(values, duplication_threshold):
            if limit > 0 and len(values) > limit:
                values = random.sample(values, limit)
            return {
                "type": "values",
                "data": values
            }
        # use weighted values
        weighted_values = calculate_weights(values)
        if sample_weights:
            weighted_values = top_n_items(weighted_values, limit)
        return {
            "type": "values",
            "data": weighted_values
        }


class IntStringValueAnalyzer(ValueListAnalyzer):
    def compatibility_score(self, values: Generator[Any, None, None]) -> float:
        if all_match_pattern(INT_STRING_PATTERN, values):
            return ValueListAnalyzer.MOSTLY_COMPATIBLE + 0.01
        return ValueListAnalyzer.NOT_COMPATIBLE

    def generate_spec(self, name: str, values: List[Any], refs: RefsAggregator, **kwargs) -> Dict[str, Any]:
        spec = generate_numeric_spec([int(v) for v in values], kwargs.get('limit', 0))
        if "config" not in spec:
            spec["config"] = {}
        spec["config"]["cast"] = "str"
        return spec


class UuidValueAnalyzer(ValueListAnalyzer):
    def compatibility_score(self, values: Generator[Any, None, None]) -> float:
        if all_match_pattern(UUID_PATTERN, values):
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


def compute_str_list_spec(values: list) -> dict:
    """
    Creates string spec from lists of list of strings
    Args:
        values: list of lists of strings

    Returns:
        (dict): with appropriate string spec
    """

    weights = calculate_list_size_weights(values)
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


@datacraft.registry.analyzers('int-string')
def _int_string_analyzer() -> datacraft.ValueListAnalyzer:
    return IntStringValueAnalyzer()


@datacraft.registry.analyzers('uuid')
def _uuid_analyzer() -> datacraft.ValueListAnalyzer:
    return UuidValueAnalyzer()
