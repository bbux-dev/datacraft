"""module for distribution type datacraft registry functions"""
import json
import logging

import datacraft
from . import common
from . import schemas

_log = logging.getLogger(__name__)
_DISTRIBUTION_KEY = 'distribution'


@datacraft.registry.schemas(_DISTRIBUTION_KEY)
def _get_distribution_schema():
    """ get the schema for distribution type """
    return schemas.load(_DISTRIBUTION_KEY)


@datacraft.registry.types(_DISTRIBUTION_KEY)
def _configure_distribution_supplier(field_spec, _):
    """ configure the supplier for distribution types """
    if 'data' not in field_spec:
        raise datacraft.SpecException(
            'required data element not defined for ' + _DISTRIBUTION_KEY + ' type : ' + json.dumps(field_spec))
    distribution = datacraft.distributions.from_string(field_spec['data'])
    return datacraft.suppliers.distribution_supplier(distribution)


@datacraft.registry.usage(_DISTRIBUTION_KEY)
def _example_distribution_usage():
    example_one = {
        "values": {
            "type": "distribution",
            "data": "uniform(start=10, end=30)"
        }
    }
    example_two = {
        "age": {
            "type": "distribution",
            "data": "normal(mean=28, stddev=10, min=18, max=40)",
            "config": {"cast": "int"}
        }
    }
    example_tre = {
        "pressure": {
            "type": "distribution",
            "data": "gauss(mean=33, stddev=3.4756535)",
            "config": {
                "count_dist": "normal(mean=2, stddev=1, min=1, max=4)",
                "as_list": True
            }
        }
    }
    examples = [example_one, example_two, example_tre]
    clis = [common.standard_cli_example_usage(example, 3) for example in examples]
    apis = [common.standard_api_example_usage(example, 3) for example in examples]
    return {
        'cli': '\n'.join(clis),
        'api': '\n'.join(apis)
    }
