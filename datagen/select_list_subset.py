"""
Module for select_list_subset type
"""
import json

from . import types, utils, suppliers, schemas
from .exceptions import SpecException

_SELECT_LIST_SUBSET_KEY = 'select_list_subset'


@types.registry.schemas(_SELECT_LIST_SUBSET_KEY)
def _select_list_subset_schema():
    return schemas.load(_SELECT_LIST_SUBSET_KEY)


@types.registry.types(_SELECT_LIST_SUBSET_KEY)
def _configure_supplier(field_spec, loader):
    """ configures supplier for select_list_subset type """
    config = utils.load_config(field_spec, loader)
    if config is None or ('mean' not in config and 'count' not in config):
        raise SpecException('Config with mean or count defined must be provided: %s' % json.dumps(field_spec))
    if 'ref' in field_spec and 'data' in field_spec:
        raise SpecException('Only one of "data" or "ref" can be provided for: %s' % json.dumps(field_spec))

    if 'ref' in field_spec:
        ref_name = field_spec.get('ref')
        field_spec = loader.get_ref_spec(ref_name)
        if field_spec is None:
            raise SpecException('No ref with name %s found: %s' % (ref_name, json.dumps(field_spec)))

        if 'data' in field_spec:
            data = field_spec.get('data')
        else:
            data = field_spec
    elif 'data' in field_spec:
        data = field_spec.get('data')
    if utils.any_key_exists(config, ['mean', 'stddev']):
        return suppliers.list_stat_sampler(data, config)
    return suppliers.list_count_sampler(data, config)
