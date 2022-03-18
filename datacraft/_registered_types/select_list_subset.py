import json
import logging

import datacraft
from . import schemas

_log = logging.getLogger(__name__)
_SELECT_LIST_SUBSET_KEY = 'select_list_subset'
# alias
_SAMPLE_KEY = 'sample'


@datacraft.registry.schemas(_SAMPLE_KEY)
@datacraft.registry.schemas(_SELECT_LIST_SUBSET_KEY)
def _select_list_subset_schema():
    """ schema for select_list_subset type """
    return schemas.load(_SELECT_LIST_SUBSET_KEY)


@datacraft.registry.types(_SAMPLE_KEY)
@datacraft.registry.types(_SELECT_LIST_SUBSET_KEY)
def _configure_select_list_subset_supplier(field_spec, loader):
    """ configures supplier for select_list_subset type """
    config = datacraft.utils.load_config(field_spec, loader)
    data = None
    if config is None or ('mean' not in config and 'count' not in config):
        raise datacraft.SpecException('Config with mean or count defined must be provided: %s' % json.dumps(field_spec))
    if 'ref' in field_spec and 'data' in field_spec:
        raise datacraft.SpecException('Only one of "data" or "ref" can be provided for: %s' % json.dumps(field_spec))

    if 'ref' in field_spec:
        ref_name = field_spec.get('ref')
        field_spec = loader.get_ref(ref_name)
        if field_spec is None:
            raise datacraft.SpecException('No ref with name %s found: %s' % (ref_name, json.dumps(field_spec)))

        if 'data' in field_spec:
            data = field_spec.get('data')
        else:
            data = field_spec
    elif 'data' in field_spec:
        data = field_spec.get('data')
    if data is None:
        raise datacraft.SpecException(
            'Unable to identify data for ' + _SELECT_LIST_SUBSET_KEY + ' for spec: ' + json.dumps(field_spec))
    return datacraft.suppliers.select_list_subset(data, **config)
