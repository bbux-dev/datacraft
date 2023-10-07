from typing import List, Any, Dict, Generator

import datacraft
from datacraft import ValueListAnalyzer, RefsAggregator

TEST_VALUES = ["~7~", "~D~", "~P~"]


class AnalyzerForTestOnly(ValueListAnalyzer):
    def __init__(self, test_values):
        self.test_values = test_values

    def compatibility_score(self, values: Generator[Any, None, None]) -> float:
        all_values = list(values)
        # don't want to try to sort non string items
        if any(not isinstance(v, str) for v in all_values):
            return ValueListAnalyzer.NOT_COMPATIBLE
        # make sure we don't interfere with other analyzers, only match on the test values
        if sorted(all_values) == sorted(self.test_values):
            return ValueListAnalyzer.TOTALLY_COMPATIBLE
        return ValueListAnalyzer.NOT_COMPATIBLE

    def generate_spec(self, name: str, values: List[Any], refs: RefsAggregator, **kwargs) -> Dict[str, Any]:
        refs.add("one", {"fake": "spec"})
        return {"fake": "spec"}


@datacraft.registry.analyzers("test_it")
def _test_analyzer():
    return AnalyzerForTestOnly(TEST_VALUES)


def test_refs_populated():
    examples = [{"val": v} for v in TEST_VALUES]

    spec = datacraft.infer.from_examples(examples)
    assert "refs" in spec
