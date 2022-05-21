import json
import logging

import datacraft
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
