import pandas as pd  # type: ignore
from collections import Counter
from typing import Any, Dict, Generator, List, Union, Callable

_LOOKUP = {
    True: "_TRUE_",
    False: "_FALSE_",
    None: "_NONE_"
}


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


def _requires_substitution(values):
    return _is_boolean(values) or _any_is_none(values)


def _substitute(values):
    return [_LOOKUP.get(v, v) for v in values]


def _is_numeric(values):
    return all((isinstance(value, (int, float)) and not isinstance(value, bool)) for value in values)


def _all_lists_numeric(values):
    return all(_is_numeric(sublist) for sublist in values)


def _all_lists_of_type(lists, type_check):
    return all(isinstance(val, type_check) for sublist in lists for val in sublist)


def _is_boolean(values):
    return all(isinstance(value, bool) for value in values)


def _any_is_none(values):
    return any(v is None for v in values)


def _compute_range(values: List[Union[int, float]]) -> Dict[str, Any]:
    """
    Compute the range from a list of numeric values.

    Args:
        values (List[Union[int, float]]): A list of numeric values.

    Returns:
        Dict[str, Any]: A dictionary with the structure:
            {
                "type": "rand_range",
                "data": [min, max]
            }
    """
    if not _is_numeric(values):
        raise ValueError("All values in the list must be numeric.")

    type_key = "rand_range"
    if all(isinstance(value, int) for value in values):
        type_key = "rand_int_range"

    return {
        "type": type_key,
        "data": [min(values), max(values)]
    }


def _compute_list_range(values: list) -> dict:
    """
    Creates rand_range spec for lists of values
    Args:
        values: list of lists of values

    Returns:
        (dict): rand_range or rand_int_range spec
    """
    max_value = max(num for sublist in values for num in sublist)
    min_value = min(num for sublist in values for num in sublist)

    weights = _caclulate_list_size_weights(values)

    if _all_lists_of_type(values, int):
        field_type = "rand_int_range"
    else:
        field_type = "rand_range"

    return {
        "type": field_type,
        "data": [min_value, max_value],
        "config": {"count": weights, "as_list": True}
    }


def _caclulate_list_size_weights(values):
    # Calculate the frequency of each sublist length
    length_freq = Counter(len(sublist) for sublist in values)
    # Calculate the total number of lists
    total_lists = len(values)
    # Calculate the weights for each sublist length
    weights = {str(length): freq / total_lists for length, freq in length_freq.items()}
    return weights


def _compute_str_list_spec(values: list) -> dict:
    """
    Creates string spec from lists of list of strings
    Args:
        values: list of lists of strings

    Returns:
        (dict): with appropriate string spec
    """

    weights = _caclulate_list_size_weights(values)
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


def _calculate_weights(values: List[str]) -> Dict[str, float]:
    """
    Calculate the weights of occurrences of values from a list.

    Args:
        values (List[str]): A list of string values.

    Returns:
        Dict[str, float]: A dictionary containing each unique value from the list as the key
                          and its corresponding weight (or relative frequency) as the value.
    """
    total_count = len(values)
    counts = Counter(values)

    return {key: count / total_count for key, count in counts.items()}


def _are_values_unique(values: List) -> bool:
    """
    Check if all values in the list are unique.

    Args:
        values (List): A list of values.

    Returns:
        bool: True if all values are unique, otherwise False.
    """
    return len(values) == len(set(values))


def _all_list_is_str(lists):
    return all(isinstance(val, str) for sublist in lists for val in sublist)


def compute_spec(values: List[Any]):
    """
    Compute spec from list of values
    Args:
        values: List of values accumulated for leaf node

    Returns:
        Dict[str, Any]: A dictionary with the inferred spec for the values
    """
    # insert mechanism here to elegantly handle all the types of lists of values
    # there shouldn't be
    # handle leaf nodes that are lists
    if isinstance(values, list) and isinstance(values[0], list):
        if _is_numeric(values[0]):
            return _compute_list_range(values)
        if _all_list_is_str(values):
            return _compute_str_list_spec(values)
        return {
            "type": "values",
            "data": values
        }
    if len(set(values)) > 1 and _is_numeric(values):
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
    return _process_jsons(examples, func=compute_spec)


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
