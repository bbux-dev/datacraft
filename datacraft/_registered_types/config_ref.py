"""module for config_ref type datacraft registry functions"""
import logging

import datacraft

_log = logging.getLogger(__name__)
_CONFIG_REF_KEY = 'config_ref'


@datacraft.registry.types(_CONFIG_REF_KEY)
def _config_ref_handler(_, __):
    """" Does nothing, just place holder """


@datacraft.registry.usage(_CONFIG_REF_KEY)
def _example_usage():
    return "See csv type"
