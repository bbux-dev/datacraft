from abc import ABC, abstractmethod

import pandas as pd  # type: ignore
from typing import Any, Dict, Generator, List, Union, Callable

from . import registries


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

    def leaf_nodes(self, node: Union[_TreeNode, None] = None) -> Generator[_TreeNode, None, None]:
        """
        Generator to iterate over the leaf nodes of the tree.

        Args:
            node (_TreeNode, optional): Node at which to start iteration. Defaults to the root.

        Yields:
            _TreeNode: Next leaf node in the tree.
        """
        if node is None:
            node = self.root

        if node.is_leaf():
            yield node
        else:
            for child in node.children.values():
                yield from self.leaf_nodes(child)

    def to_dict(self,
                node: Union[_TreeNode, None] = None,
                func: Union[Callable, None] = None) -> Dict[str, Any]:
        """
        Convert the tree or subtree to a dictionary.

        Args:
            node (_TreeNode, optional): Node at which to start conversion. Defaults to the root.
            func (Callable, optional): Function to apply on leaf node values. If provided,
                                       this function is applied to the list of values at each
                                       leaf node before they are returned.

        Returns:
            Dict[str, Any]: Dictionary representation of the tree or subtree.
        """
        if node is None:
            node = self.root

        if node.is_leaf():
            return func(node.values) if func else node.values

        data = {}
        for key, child in node.children.items():
            data[key] = self.to_dict(child, func)
        return data

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
            return func(node.values) if func else node.values

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
    tree = _Tree()
    for data in jsons:
        tree.insert(data)

    return tree.to_spec(func=func)


class ValueListAnalyzer(ABC):
    """Interface class for implementations that infer a Field Spec from a list of values"""
    @abstractmethod
    def is_compatible(self, values: Generator[Any, None, None]) -> bool:
        """
        Check if the analyzer is compatible with the provided values.

        Args:
            values (Generator[Any, None, None]): Generator producing values to check.

        Returns:
            bool: True if the analyzer can handle the values, otherwise False.
        """
        raise NotImplementedError

    @abstractmethod
    def generate_spec(self, values: List[Any]) -> Dict[str, Any]:
        """
        Generate a specification for the provided list of values.

        Args:
            values (List[Any]): List of values to generate the spec for.

        Returns:
            Dict[str, Any]: A dictionary with the inferred spec for the values.
        """
        raise NotImplementedError


def _lookup_handler(values: List[Any]):
    analyzer = registries.lookup_analyzer("default")
    if analyzer is None:
        raise LookupError("Unable to find default analyzer")
    for key in registries.registered_analyzers():
        if key == "default":
            continue
        analyzer = registries.lookup_analyzer(key)
        if analyzer is None or not isinstance(analyzer, ValueListAnalyzer):
            raise LookupError(f"Analyzer with name {key} registered but not valid: {analyzer}")
        if analyzer.is_compatible(v for v in values):
            return analyzer
    return analyzer.generate_spec(values)


def from_examples(examples: List[dict]) -> dict:
    """
    Generates a Data Spec from the list of example JSON records
    Args:
        examples (list): Data to infer Data Spec from

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
    return _process_jsons(examples, _lookup_handler)


def csv_to_spec(file_path: str) -> Dict[str, Union[str, Dict]]:
    """
    Read a CSV from the provided file path, convert it to JSON records,
    and then pass it to the from_examples function to get the spec.

    Args:
        file_path (str): The path to the CSV file.

    Returns:
        Dict[str, Union[str, Dict]]: The inferred data spec from the CSV data.
    """
    # Read CSV using pandas
    df = pd.read_csv(file_path)

    # Convert DataFrame to list of JSON records
    json_records = df.to_dict(orient='records')

    # Get the spec using from_examples function
    return from_examples(json_records)
