"""exercise all the different variations for count specification for multiple types"""
import json
import pytest
import datacraft

from . import builder

VALUES_SPECS = [
    (builder.values([1, 2, 3]), 2),
    (builder.values("one"),     2),
    (builder.values({"one": 0.7, "two": 0.3}, prefix="@"), 2),

    (builder.values([1, 2, 3]), 5),
    (builder.values("one"),     5),
    (builder.values({"one": 0.7, "two": 0.3}, prefix="@"), 5)
]


@pytest.mark.parametrize("field_spec, count", VALUES_SPECS)
def test_count_values(field_spec, count):
    if 'config' in field_spec:
        field_spec['config']['count'] = count
    else:
        field_spec['config'] = {'count': count}
    entries = datacraft.entries({"field": field_spec}, 2)
    values = [entry['field'] for entry in entries]
    for value in values:
        assert isinstance(value, list), "Spec " + json.dumps(field_spec) + " did not create list type in output"
        assert len(value) == count, "Spec " + json.dumps(field_spec) + " did not create list of size 2s"
