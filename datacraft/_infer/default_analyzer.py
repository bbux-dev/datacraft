from typing import Generator, Any, List, Dict
import random
import datacraft
from datacraft import ValueListAnalyzer, RefsAggregator
from .helpers import (is_nested_lists, all_is_numeric, all_list_is_str,
                      requires_substitution, substitute, are_values_unique,
                      calculate_weights, top_n_items)
from .num_analyzers import compute_range, compute_list_range
from .str_analyzers import compute_str_list_spec


class DefaultValueAnalyzer(ValueListAnalyzer):
    """ when nothing else works """

    def compatibility_score(self, values: Generator[Any, None, None]) -> float:
        return ValueListAnalyzer.MOSTLY_COMPATIBLE

    def generate_spec(self, name: str, values: List[Any], refs: RefsAggregator, **kwargs) -> Dict[str, Any]:
        # insert mechanism here to elegantly handle all the types of lists of values
        # handle leaf nodes that are lists
        if is_nested_lists(v for v in values):
            if all_is_numeric(values[0]):
                return compute_list_range(values)
            if all_list_is_str(values):
                return compute_str_list_spec(values)
            return {
                "type": "values",
                "data": values
            }
        if len(set(values)) > 1 and all_is_numeric(values):
            return compute_range(values)
        if requires_substitution(values):
            values = substitute(values)

        limit = kwargs.get('limit', 0)
        sample_weights = kwargs.get('limit_weighted', False)

        # unique values, just rotate through them
        if are_values_unique(values):
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


@datacraft.registry.analyzers('default')
def _default_analyzer() -> datacraft.ValueListAnalyzer:
    return DefaultValueAnalyzer()
