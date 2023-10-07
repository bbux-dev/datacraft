"""Looks for common data strings"""
from typing import Generator, List, Any, Dict, Pattern

from datacraft import ValueListAnalyzer, RefsAggregator


class RegexStringAnalyzer(ValueListAnalyzer):

    def __init__(self, key_to_pattern: Dict[str, Pattern]):
        self.key_to_pattern = key_to_pattern

    def compatibility_score(self, values: Generator[str, None, None]) -> float:
        for value in values:
            if not isinstance(value, str):
                return 0.0
            if not any(p.match(value) for p in self.key_to_pattern.values()):
                return 0.0
        return ValueListAnalyzer.TOTALLY_COMPATIBLE

    def generate_spec(self, name: str, values: List[Any], refs: RefsAggregator, **kwargs) -> Dict[str, Any]:
        counts = count_regex_matches(values, self.key_to_pattern)
        if len(counts) == 1:
            field_type = next(iter(counts))
            return {
                "type": field_type
            }
        total = sum(v for v in counts.values())
        weighted = {k: v/total for k, v in counts.items()}

        weighted_refs = {}
        for idx, (field_type, weight) in enumerate(weighted.items()):
            spec = {
                "type": field_type
            }
            ref_key = f'{name}_ref{idx}'
            refs.add(ref_key, spec)
            weighted_refs[ref_key] = weight

        return {
            "type": "weighted_ref",
            "data": weighted_refs
        }


def count_regex_matches(values: List[str], patterns: Dict[str, Pattern]) -> Dict[str, int]:
    """
    Count the matches for each regex pattern in the list of values.

    Args:
        values (List[str]): A list of string values.
        patterns (Dict[str, Pattern]): A dictionary of "key" -> regex pattern.

    Returns:
        Dict[str, int]: A dictionary of "key" -> count of matches.
    """

    # Initialize count dictionary
    counts = {key: 0 for key in patterns}

    # Count matches for each value and each pattern
    for value in values:
        for key, pattern in patterns.items():
            if pattern.match(value):
                counts[key] += 1

    # remove zero counts
    counts = {k: v for k, v in counts.items() if v > 0}
    return counts
