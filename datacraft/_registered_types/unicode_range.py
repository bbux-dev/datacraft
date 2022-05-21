import json
import logging

import datacraft
from . import schemas

_log = logging.getLogger(__name__)
_UNICODE_RANGE_KEY = 'unicode_range'


@datacraft.registry.schemas(_UNICODE_RANGE_KEY)
def _get_unicode_range_schema():
    """ get the unicode range schema """
    return schemas.load(_UNICODE_RANGE_KEY)


@datacraft.registry.types(_UNICODE_RANGE_KEY)
def _configure_unicode_range_supplier(spec, loader):
    """ configure the supplier for unicode_range types """
    if 'data' not in spec:
        raise datacraft.SpecException('data is Required Element for unicode_range specs: ' + json.dumps(spec))
    data = spec['data']
    if not isinstance(data, list):
        raise datacraft.SpecException(
            f'data should be a list or list of lists with two elements for {_UNICODE_RANGE_KEY} specs: ' + json.dumps(
                spec))
    config = datacraft.utils.load_config(spec, loader)
    return datacraft.suppliers.unicode_range(data, **config)
