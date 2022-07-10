"""module for network type datacraft registry functions"""
import json
import logging

import datacraft
from . import common
from . import schemas

_log = logging.getLogger(__name__)
_IP_KEY = 'ip'
_IPV4_KEY = 'ipv4'
_IP_PRECISE_KEY = 'ip.precise'
_NET_MAC_KEY = 'net.mac'


@datacraft.registry.schemas(_IP_KEY)
def _get_ip_schema():
    """ returns the schema for the ip types """
    return schemas.load(_IP_KEY)


@datacraft.registry.schemas(_IPV4_KEY)
def _get_ipv4_schema():
    """ returns the schema for the ipv4 types """
    # shares schema with ip
    return schemas.load(_IP_KEY)


@datacraft.registry.schemas(_IP_PRECISE_KEY)
def _get_ip_precise_schema():
    """ returns the schema for the ip.precise types """
    return schemas.load(_IP_PRECISE_KEY)


@datacraft.registry.schemas(_NET_MAC_KEY)
def _get_mac_addr_schema():
    """ returns the schema for the net.mac types """
    return schemas.load(_NET_MAC_KEY)


@datacraft.registry.types(_IPV4_KEY)
@datacraft.registry.types(_IP_KEY)
def _configure_ip(field_spec, loader):
    """ configures value supplier for ip type """
    config = datacraft.utils.load_config(field_spec, loader)
    try:
        return datacraft.suppliers.ip_supplier(**config)
    except ValueError as err:
        raise datacraft.SpecException(str(err)) from err


@datacraft.registry.types(_IP_PRECISE_KEY)
def _configure_precise_ip(field_spec, _):
    """ configures value supplier for ip.precise type """
    config = field_spec.get('config')
    if config is None:
        raise datacraft.SpecException('No config for: ' + json.dumps(field_spec) + ', param cidr required')
    cidr = config.get('cidr')
    sample = datacraft.utils.is_affirmative('sample', config, 'no')
    if cidr is None:
        raise datacraft.SpecException('Invalid config for: ' + json.dumps(field_spec) + ', param cidr required')
    return datacraft.suppliers.ip_precise(cidr, sample)


@datacraft.registry.types(_NET_MAC_KEY)
def _configure_mac_address_supplier(field_spec, loader):
    """ configures value supplier for net.mac type """
    config = datacraft.utils.load_config(field_spec, loader)
    if datacraft.utils.is_affirmative('dashes', config):
        delim = '-'
    else:
        delim = datacraft.registries.get_default('mac_addr_separator')

    return datacraft.suppliers.mac_address(delim)


@datacraft.registry.usage(_IP_KEY)
def _example_ip_usage():
    return "Alias for ipv4"


@datacraft.registry.usage(_IPV4_KEY)
def _example_ipv4_usage():
    example = {
        "network": {
            "type": _IPV4_KEY,
            "config": {
                "cidr": "2.22.222.0/16"
            }
        }
    }
    return common.standard_example_usage(example, 3)


@datacraft.registry.usage(_IP_PRECISE_KEY)
def _example_ip_precise_usage():
    example = {
        "network": {
            "type": _IP_PRECISE_KEY,
            "config": {
                "cidr": "192.168.0.0/14",
                "sample": "true"
            }
        }
    }
    return common.standard_example_usage(example, 3)


@datacraft.registry.usage(_NET_MAC_KEY)
def _example_net_mac_usage():
    example = {
        "network": {
            "type": _NET_MAC_KEY,
            "config": {
                "dashes": "true"
            }
        }
    }
    return common.standard_example_usage(example, 3)
