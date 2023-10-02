from typing import Generator, Any, List, Dict

import datacraft
from datacraft import ValueListAnalyzer, RefsAggregator
from .helpers import (_is_nested_lists, _all_is_numeric, _all_list_is_str,
                      _requires_substitution, _substitute, _are_values_unique, _calculate_weights)
from .num_analyzers import _compute_range, _compute_list_range
from .str_analyzers import _compute_str_list_spec


class DefaultValueAnalyzer(ValueListAnalyzer):
    """ when nothing else works """

    def compatibility_score(self, values: Generator[Any, None, None]) -> float:
        return ValueListAnalyzer.MOSTLY_COMPATIBLE

    def generate_spec(self, values: List[Any], refs: RefsAggregator) -> Dict[str, Any]:
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
