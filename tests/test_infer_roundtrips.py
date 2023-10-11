import json
import logging
import os

import pytest

# to trigger analyzer loading
import datacraft._infer
import datacraft
from datacraft import SpecException

log = logging.getLogger(__name__)
logging.basicConfig(format='%(levelname)s %(message)s',
                    level=logging.INFO)

ASSUMED_VALID = "valid"
ASSUMED_INVALID = "invalid"
INSTANCE = "instance"
MESSAGE = "note"

root_dir = os.path.dirname(os.path.realpath(__file__))
schema_dir = os.path.realpath(os.sep.join([root_dir, '..', 'datacraft', '_registered_types', 'schema']))
tests_dir = os.sep.join([root_dir, 'data'])

TEST_FILES = [
    "values.tests.json",
    "range.tests.json",
    "combine.tests.json",
    "combine_list.tests.json",
    "uuid.tests.json",
    "char_class.tests.json",
    "date.tests.json",
    "date-epoch.tests.json",
    "geo.lat.tests.json",
    "geo.long.tests.json",
    "geo.pair.tests.json",
    "unicode_range.tests.json",
    "ip.tests.json",
    "sample.tests.json",
    "select_list_subset.tests.json",
    "calculate.tests.json",
    "csv.tests.json",
    "weighted_csv.tests.json",
    "nested.tests.json",
    "ref.tests.json",
    "ref_list.tests.json",
    "weighted_ref.tests.json",
    "distribution.tests.json",
    "templated.tests.json"
]


@pytest.mark.parametrize("test_file_name", TEST_FILES)
def test_infer_round_trip(test_file_name):
    tests = load_test_file(test_file_name)
    for file, type_tests in tests.items():
        field_type = file.replace('.schema.json', '')
        if 'EXAMPLE' in file:
            continue
        for example in type_tests[ASSUMED_VALID]:
            raw_spec = {'field': example[INSTANCE]}
            if 'combine' in field_type:
                raw_spec['refs'] = {'one': 1, 'two': 2, 'tre': 3}
            try:
                records = datacraft.entries(raw_spec, 10)
                infer_spec = datacraft.infer.from_examples(records)
                distance = dict_distance(raw_spec, infer_spec)
                print(f'{field_type}:{distance}')
            except SpecException as se:
                print(f"{field_type}: ERROR: {se}, {json.dumps(example[INSTANCE])}")
            except Exception as e:
                print(f'{field_type}: ERROR: {e}')


def load_test_file(file_name):
    return _load_file(tests_dir, file_name)


def _load_file(root_dir, file_name):
    with open(os.sep.join([root_dir, file_name]), 'r') as handle:
        return json.load(handle)


def jaccard_distance(set1, set2):
    """
    Compute the Jaccard distance between two sets.

    Jaccard distance = 1 - (size of intersection / size of union)
    """
    intersection_len = len(set1.intersection(set2))
    union_len = len(set1.union(set2))

    if union_len == 0:
        return 0.0

    return 1 - (intersection_len / union_len)


def compute_distance(val1, val2):
    """
    Compute distance between two values.
    """
    if isinstance(val1, dict) and isinstance(val2, dict):
        return dict_distance(val1, val2)

    if isinstance(val1, list) and isinstance(val2, list):
        return jaccard_distance(set(val1), set(val2))

    return 0 if val1 == val2 else 1


def dict_distance(dict1, dict2):
    """
    Compute a distance between two dictionaries.
    """
    all_keys = set(dict1.keys()).union(dict2.keys())
    total_distance = 0

    for key in all_keys:
        val1 = dict1.get(key)
        val2 = dict2.get(key)

        total_distance += compute_distance(val1, val2)

    # Normalize by the number of keys.
    return total_distance / len(all_keys)