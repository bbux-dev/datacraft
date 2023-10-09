import json
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Generator, List, Union, Callable

from . import registries

_log = logging.getLogger(__name__)


class _TreeNode:
    def __init__(self, key: Union[str, None] = None):
        """
        _TreeNode initialization.

        Args:
            key (str, optional): Key for the current tree node. Defaults to None.
        """
        self.key = key
        self.children: Dict[str, '_TreeNode'] = {}
        self.values: List[Union[int, float, str, list, None]] = []

    def is_leaf(self) -> bool:
        """
        Check if the node is a leaf node.

        Returns:
            bool: True if the node is leaf, otherwise False.
        """
        return len(self.children) == 0


class _Tree:
    def __init__(self):
        """_Tree initialization."""
        self.root = _TreeNode()

    def insert(self,
               data_dict: Dict[str, Any],
               node: Union[_TreeNode, None] = None) -> None:
        """
        Insert data into the tree.

        Args:
            data_dict (Dict[str, Any]): Dictionary containing data to insert.
            node (_TreeNode, optional): Node at which to start insertion. Defaults to the root.
        """
        if node is None:
            node = self.root

        for key, value in data_dict.items():
            if key not in node.children:
                node.children[key] = _TreeNode(key=key)

            if isinstance(value, (int, float, str, list, bool)) or value is None:
                node.children[key].values.append(value)
            else:
                self.insert(value, node=node.children[key])

    def to_spec(self,
                node: Union[_TreeNode, None] = None,
                func: Union[Callable, None] = None) -> dict:
        """
        Convert the tree or subtree to a Data Spec.

        Args:
            node (_TreeNode, optional): Node at which to start conversion. Defaults to the root.
            func (Callable, optional): Function to apply on leaf node values. If provided,
                                       this function is applied to the list of values at each
                                       leaf node before they are returned.

        Returns:
            Dict[str, Any]: Dictionary representation Data Spec.
        """
        if node is None:
            node = self.root

        if node.is_leaf():
            return func(node.key, node.values) if func else node.values

        data = {}
        for key, child in node.children.items():
            if child.is_leaf():
                data[key] = self.to_spec(child, func)
            else:
                data[key] = {
                    "type": "nested",
                    "fields": self.to_spec(child, func)
                }

        return data


def _process_jsons(jsons: List[Dict[str, Any]],
                   func: Union[Callable, None] = None) -> dict:
    """
    Process a list of JSON data, print the leaf nodes, and return a Data Spec of the tree.

    Args:
        jsons (List[Dict[str, Any]]): List of JSON data to process.
        func (Callable, optional): Function to apply on leaf node values. If provided,
                                   this function is applied to the list of values at each
                                   leaf node before they are returned.

    Returns:
        str: Data Spec from the tree.
    """
    if not isinstance(jsons, list) or not isinstance(jsons[0], dict):
        raise ValueError("Expected List of Dictionaries to infer data from")
    tree = _Tree()
    for data in jsons:
        tree.insert(data)

    return tree.to_spec(func=func)


class RefsAggregator:
    """Class for adding references to when building inferred specs"""
    refs = {}  # type: dict

    def add(self, key: str, val: dict):
        """Add spec to refs section with given key/name

        Args:
            key: Name used to reference this spec
            val: Field Spec for this key/name
        """
        if key in self.refs:
            _log.warning("Key %s already in refs: %s, replacing with %s",
                         key, json.dumps(self.refs.get(key)),
                         json.dumps(val))
        self.refs[key] = val


class ValueListAnalyzer(ABC):
    """Interface class for implementations that infer a Field Spec from a list of values"""
    NOT_COMPATIBLE = 0
    SOMEWHAT_COMPATIBLE = 0.25
    MOSTLY_COMPATIBLE = 0.5
    HIGHLY_COMPATIBLE = 0.75
    TOTALLY_COMPATIBLE = 1.0

    @abstractmethod
    def compatibility_score(self, values: Generator[Any, None, None]) -> float:
        """
        Check if the analyzer is compatible with the provided values.

        Args:
            values (Generator[Any, None, None]): Generator producing values to check.

        Returns:
            int: 0, for not compatible with steps up to 1 for fully and totally compatible
        """
        raise NotImplementedError

    @abstractmethod
    def generate_spec(self, name: str,
                      values: List[Any],
                      refs: RefsAggregator,
                      **kwargs) -> Dict[str, Any]:
        """
        Generate a specification for the provided list of values. Adds any necessary refs
        to refs aggregator as needed.

        Args:
            name: name of field this spec is being generated for
            values: List of values to generate the spec for.
            refs: for adding refs if needed for generated spec.

        Keyword Args:
            limit: for lists or weighted values, down sample to this size if needed
            limit_weighted: take top N limit weights

        Returns:
            Dict[str, Any]: A dictionary with the inferred spec for the values.
        """
        raise NotImplementedError


class _LookupHandler:
    ref_agg = RefsAggregator()

    def __init__(self, **kwargs):
        self.limit = kwargs.get('limit', 0)
        self.limit_weighted = kwargs.get('limit_weighted', False)

    def handle(self, name: str, values: List[Any]):
        analyzer = registries.lookup_analyzer("default")
        top_score = ValueListAnalyzer.SOMEWHAT_COMPATIBLE

        if analyzer is None:
            raise LookupError("Unable to find default analyzer")
        candidates = []
        for key in registries.registered_analyzers():
            if key == "default":
                continue
            candidate = registries.lookup_analyzer(key)
            if candidate is None or not isinstance(candidate, ValueListAnalyzer):
                raise LookupError(f"Analyzer with name {key} registered but not valid: {analyzer}")
            score = candidate.compatibility_score(v for v in values)
            if score > 0:
                candidates.append((candidate, score))
        try:
            # pick one with the highest score, first one that is
            analyzer, top_score = max(candidates, key=lambda x: x[1])
        except ValueError:
            # empty list
            pass

        _log.debug("%s %s %s",
                   f"Field: {name}".ljust(20),
                   f"Analyzing with {analyzer.__class__.__name__}".ljust(35),
                   f"Compatibility score: {top_score}".ljust(25))
        return analyzer.generate_spec(name=name,
                                      values=values,
                                      refs=self.ref_agg,
                                      limit=self.limit,
                                      limit_weighted=self.limit_weighted)


def from_examples(examples: List[dict], **kwargs) -> dict:
    """
    Generates a Data Spec from the list of example JSON records

    Args:
        examples (list): Data to infer Data Spec from

    Keyword Args:
        limit (int): for lists or weighted values, down sample to this size if needed
        limit_weighted (bool): take top N limit weights

    Returns:
        dict: Data Spec as dictionary

    Examples:
        >>> import datacraft.infer as infer
        >>> xmpls = [
        ...     {"foo": {"bar": 22.3, "baz": "single"}},
        ...     {"foo": {"bar": 44.5, "baz": "double"}}
        ... ]
        >>>
        >>> infer.from_examples(xmpls)
        {'foo': {'type': 'nested', 'fields': {'bar': {'type': 'rand_range', 'data': [22.3, 44.5]}, 'baz': {'type': 'values', 'data': ['single', 'double']}}}}
    """
    if examples is None or len(examples) == 0:
        return {}
    handler = _LookupHandler(**kwargs)
    raw_spec = _process_jsons(examples, handler.handle)
    if len(handler.ref_agg.refs) > 0:
        raw_spec["refs"] = handler.ref_agg.refs
    return raw_spec


def csv_to_spec(file_path: str, **kwargs) -> Union[None, dict]:
    """
    Read a CSV from the provided file path, convert it to JSON records,
    and then pass it to the from_examples function to get the spec.

    Args:
        file_path (str): The path to the CSV file.

    Keyword Args:
        limit (int): for lists or weighted values, down sample to this size if needed
        limit_weighted (bool): take top N limit weights

    Returns:
        Dict[str, Union[str, Dict]]: The inferred data spec from the CSV data.
    """
    try:
        import pandas  # type: ignore
        import numpy as np
    except ModuleNotFoundError:
        _log.error('pandas or numpy not installed, please pip/conda install these to allow analysis of csv files')
        return None
    # Read CSV using pandas
    df = pandas.read_csv(file_path)
    df = df.replace({np.nan: None})

    # Convert DataFrame to list of JSON records
    json_records = df.to_dict(orient='records')

    # Get the spec using from_examples function
    return from_examples(json_records, **kwargs)
