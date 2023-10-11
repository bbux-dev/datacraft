""" module for analyzers looking for geographic entities """
import math
from typing import List, Any, Dict, Generator

import datacraft
from datacraft import RefsAggregator, ValueListAnalyzer


class SimpleLatLongAnalyzer(ValueListAnalyzer):
    def compatibility_score(self, values: Generator[Any, None, None]) -> float:
        count = 0
        for val in values:
            if not isinstance(val, float):
                return ValueListAnalyzer.NOT_COMPATIBLE
            if val < -180 or val > 180.0:
                return ValueListAnalyzer.NOT_COMPATIBLE
            count += 1
        count_bonus = _calculate_bonus_score(count)
        return ValueListAnalyzer.MOSTLY_COMPATIBLE + count_bonus

    def generate_spec(self, name: str, values: List[Any], refs: RefsAggregator, **kwargs) -> Dict[str, Any]:
        max_value = max(values)
        min_value = min(values)
        # assume latitude
        if min_value >= -90.0 and max_value <= 90.0:
            return {
                "type": "geo.lat"
            }
        # must be longitude:
        return {
            "type": "geo.long"
        }


def _calculate_bonus_score(count):
    """maps the log base 10 of the count to a value between -0.25 and 0.25
    Penalized if not enough examples to assess by

    Args:
        count: number of records assessed

    Returns:
        the bonus score
    """
    if count <= 0:
        raise ValueError("Count must be greater than 0")

    log_val = math.log10(count)

    # Map the log value to the desired range
    if log_val <= 1:
        return -0.25
    elif log_val <= 2:
        return 0.01
    elif log_val <= 3:
        return 0.1
    elif log_val <= 4:
        return 0.2
    else:
        return 0.25


@datacraft.registry.analyzers('geo.simple-lat-long')
def _lat_long_analyzer() -> datacraft.ValueListAnalyzer:
    return SimpleLatLongAnalyzer()
