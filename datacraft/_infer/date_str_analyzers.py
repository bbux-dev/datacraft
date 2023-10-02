"""Looks for common data strings"""
import re
from typing import Generator, List, Any, Dict, Pattern

import datacraft
from datacraft import ValueListAnalyzer, RefsAggregator

# Regular expression patterns for the date formats
DATE_PATTERN = re.compile(r'^\d{2}-\d{2}-\d{4}$')
DATE_ISO_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$')
DATE_ISO_MS_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}$')
DATE_ISO_US_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}$')

KEY_TO_PATTERN = {
    "date": DATE_PATTERN,
    "date.iso": DATE_ISO_PATTERN,
    "date.iso.ms": DATE_ISO_MS_PATTERN,
    "date.iso.us": DATE_ISO_US_PATTERN
}


class DateStringAnalyzer(ValueListAnalyzer):

    def compatibility_score(self, values: Generator[str, None, None]) -> float:
        for value in values:
            if not isinstance(value, str):
                return 0.0
            if not (DATE_PATTERN.match(value) or
                    DATE_ISO_PATTERN.match(value) or
                    DATE_ISO_MS_PATTERN.match(value) or
                    DATE_ISO_US_PATTERN.match(value)):
                return 0.0

        return ValueListAnalyzer.TOTALLY_COMPATIBLE

    def generate_spec(self, name: str, values: List[Any], refs: RefsAggregator) -> Dict[str, Any]:
        counts = count_regex_matches(values, KEY_TO_PATTERN)
        if len(counts) == 1:
            date_type = next(iter(counts))
            return {
                "type": date_type
            }
        total = sum(v for v in counts.values())
        weighted = {k: v/total for k, v in counts.items()}

        weighted_refs = {}
        for idx, (date_type, weight) in enumerate(weighted.items()):
            spec = {
                "type": date_type
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


@datacraft.registry.analyzers('date')
def _date_analyzer() -> datacraft.ValueListAnalyzer:
    return DateStringAnalyzer()
