import json
import pytest
from jsonschema import validate
from jsonschema.exceptions import ValidationError

ASSUMED_VALID = "valid"
ASSUMED_INVALID = "invalid"


def test_run_validation():
    definitions = load_json('definitions.json')
    tests = load_json('schema.tests.json')
    should_have_failed = {}
    for file, type_tests in tests.items():
        schema = load_json(file)
        # hack for now
        schema['definitions'] = definitions['definitions']
        for should_be_valid in type_tests[ASSUMED_VALID]:
            validate(should_be_valid['test'], schema=schema)
        for should_not_be_valid in type_tests[ASSUMED_INVALID]:
            # print(json.dumps(should_not_be_valid))
            try:
                validate(should_not_be_valid['test'], schema=schema)
            except ValidationError:
                continue
            failed_for_file = should_have_failed.get(file)
            if failed_for_file is None:
                failed_for_file = []
            failed_for_file.append(should_not_be_valid)
            should_have_failed[file] = failed_for_file
    for file, failed_for_file in should_have_failed.items():
        print(f'Should have failed but did not for {file}:')
        for should_not_be_valid in failed_for_file:
            if 'msg' in should_not_be_valid:
                print(should_not_be_valid['msg'])
            print(should_not_be_valid['test'])
    if len(should_have_failed) > 0:
        pytest.fail('Some invalid specs did not fail validation')

def test_validate_count_formats():
    definitions = load_json('definitions.json')
    schema = definitions['definitions']['count']

    bad_counts = [
        True,  # invalid count type,
        [],  # empty count type,
        [1.1, 1.7],  # counts not integers
        {},  # empty count type
        {"one": 0.7, "two": 0.3},  # bad count keys
    ]

    for bad_count in bad_counts:
        # print(json.dumps(bad_count))
        with pytest.raises(ValidationError):
            validate(bad_count, schema=schema)


def load_json(file_path):
    with open(file_path, 'r') as handle:
        return json.load(handle)
