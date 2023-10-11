def deep_sort(obj):
    """
    Recursively sort list items and nested lists in the object.

    Args:
        obj (Any): Input object (typically a dictionary).

    Returns:
        Any: Object with all its lists sorted.
    """
    if isinstance(obj, dict):
        return {k: deep_sort(v) for k, v in sorted(obj.items())}
    if isinstance(obj, list):
        # can't sort non uniform lists
        if len(set(type(v) for v in obj)) == 1:
            return sorted(deep_sort(x) for x in obj)
        return [deep_sort(x) for x in obj]
    return obj


def compare_dicts_ignore_list_order(dict1, dict2):
    """
    Compare two dictionaries deeply, ignoring the order of items in lists.

    Args:
        dict1 (dict): First dictionary.
        dict2 (dict): Second dictionary.

    Returns:
        bool: True if dictionaries are equal (ignoring order of list items), False otherwise.
    """
    return deep_sort(dict1) == deep_sort(dict2)
