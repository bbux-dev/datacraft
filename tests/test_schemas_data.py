import json
import logging
import os

import pytest
import jsonschema
from jsonschema.exceptions import ValidationError

import datacraft.registries

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
    "weighted_ref.tests.json",
    "distribution.tests.json",
    "templated.tests.json"
]


@pytest.mark.parametrize("test_file_name", TEST_FILES)
def test_run_validation(test_file_name):
    tests = load_test_file(test_file_name)
    should_have_failed = {}
    for file, type_tests in tests.items():
        # old way we used the actual file name and loaded that, now just need type name
        field_type = file.replace('.schema.json', '')
        if 'EXAMPLE' in file:
            continue
        schema = datacraft.registries.lookup_schema(field_type)
        for should_be_valid in type_tests[ASSUMED_VALID]:
            jsonschema.validate(should_be_valid[INSTANCE], schema=schema)
        for should_not_be_valid in type_tests[ASSUMED_INVALID]:
            log.debug(json.dumps(should_not_be_valid))
            try:
                jsonschema.validate(should_not_be_valid[INSTANCE], schema=schema)
            except ValidationError:
                continue
            failed_for_file = should_have_failed.get(file)
            if failed_for_file is None:
                failed_for_file = []
            failed_for_file.append(should_not_be_valid)
            should_have_failed[file] = failed_for_file
    log_should_have_failed(should_have_failed)
    if len(should_have_failed) > 0:
        pytest.fail('Some invalid specs did not fail validation')


def log_should_have_failed(should_have_failed):
    for file, failed_for_file in should_have_failed.items():
        log.warning('Should have failed but did not for %s', file)
        for should_not_be_valid in failed_for_file:
            if MESSAGE in should_not_be_valid:
                log.warning(should_not_be_valid[MESSAGE])
            log.warning(should_not_be_valid[INSTANCE])


def test_validate_count_formats():
    definitions = load_schema_file('definitions.json')
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
            jsonschema.validate(bad_count, schema=schema)


@pytest.mark.parametrize("test_file_name", TEST_FILES)
def test_spec_entries(test_file_name):
    # just testing which ones pass the schema but not creation and vise versa
    tests = load_test_file(test_file_name)
    fail_spec_exception = []
    fail_other_reason = []
    should_have_failed = []
    for file, type_tests in tests.items():
        if 'EXAMPLE' in file:
            continue
        for example in type_tests[ASSUMED_VALID]:
            spec = {'field': example[INSTANCE]}
            try:
                datacraft.entries(spec, 1)
            except datacraft.SpecException:
                fail_spec_exception.append(spec)
            except Exception:
                fail_other_reason.append(spec)
        for example in type_tests[ASSUMED_INVALID]:
            spec = {'field': example[INSTANCE]}
            try:
                datacraft.entries(spec, 1)
            except Exception:
                # that what we expected
                continue
            should_have_failed.append(spec)
    for failed in fail_spec_exception:
        log.warning(failed)
    for failed in fail_other_reason:
        log.warning(failed)
    if len(should_have_failed) > 0:
        log.warning('Specs that passed but normally fail schema validation')
        for passed in should_have_failed:
            log.warning(passed)


def load_test_file(file_name):
    return _load_file(tests_dir, file_name)


def load_schema_file(file_name):
    return _load_file(schema_dir, file_name)


def _load_file(root_dir, file_name):
    with open(os.sep.join([root_dir, file_name]), 'r') as handle:
        return json.load(handle)
