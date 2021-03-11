import json
import pytest
from jsonschema import validate
from jsonschema.exceptions import ValidationError

ASSUMED_VALID = "valid"
ASSUMED_INVALID = "invalid"

tests = {
    "combine.schema.json": {
        ASSUMED_VALID: [
            {"type": "combine", "refs": ["one", "two"]},
            {"type": "combine", "fields": ["one", "two"]},
            {"type": "combine", "refs": ["one", "two"], "config": {"join_with": " "}},
            {"type": "combine", "refs": ["one", "two"], "config": {"as_list": True}},
            {"type": "combine", "refs": ["one", "two"], "config": {"as_list": "true"}},
            {"type": "combine", "refs": ["one", "two"], "config": {"as_list": "yes"}},
            {"type": "combine", "refs": ["one", "two"], "config": {"as_list": "on"}},
        ],
        ASSUMED_INVALID: [
            {},  # empty
            {"type": "cobine"},   # misspelled
            {"type": "combine"},  # no fields or refs
            {"type": "combine", "refs": ["one"]},    # only one ref
            {"type": "combine", "fields": ["one"]},  # only one field
            {"type": "combine", "refs": ["one", "two"], "config": {"join_with": True}},  # invalid join_with param
            {"type": "combine", "refs": ["one", "two"], "config": {"as_list": "tru"}},   # invalid as_list param
        ]
    },
    "values.schema.json": {
        ASSUMED_VALID: [
            {"type": "values", "data": "constant"},
            {"type": "values", "data": ""},  # blank string still a constant
            {"type": "values", "data": 1},
            {"type": "values", "data": 1.5},
            {"type": "values", "data": True},
            {"type": "values", "data": ["one", "two"]},
            {"type": "values", "data": {"one": 0.4, "two": 0.5}},
        ],
        ASSUMED_INVALID: [
            {},  # empty
            {"type": "value"},   # misspelled
            {"type": "values"},  # no fields or refs
            {"type": "values", "test": []},  # empty data
            {"type": "values", "data": []},  # empty data
            {"type": "values", "data": {}},  # empty data
        ]
    }
}


def test_run_validation():
    with open('definitions.json', 'r') as handle:
        definitions = json.load(handle)

    for file, type_tests in tests.items():
        with open(file, 'r') as handle:
            schema = json.load(handle)
            # hack for now
            schema['definitions'] = definitions['definitions']
        for should_be_valid in type_tests[ASSUMED_VALID]:
            validate(should_be_valid, schema=schema)
        for should_not_be_valid in type_tests[ASSUMED_INVALID]:
            #print(json.dumps(should_not_be_valid))
            with pytest.raises(ValidationError) as err_info:
                validate(should_not_be_valid, schema=schema)
