"""
Module for types related to networks: ip, ipv4, ip.precise, net.mac
"""
import json

from . import types, schemas
from . import utils, suppliers
from .exceptions import SpecException
from .supplier.network import ipv4, ip_precise, mac_address

_IP_KEY = 'ip'
_IPV4_KEY = 'ipv4'
_IP_PRECISE_KEY = 'ip.precise'
_NET_MAC_KEY = 'net.mac'


@types.registry.schemas(_IP_KEY)
def _get_ip_schema():
    """ returns the schema for the ip types """
    return schemas.load(_IP_KEY)


@types.registry.schemas(_IPV4_KEY)
def _get_ipv4_schema():
    """ returns the schema for the ipv4 types """
    # shares schema with ip
    return schemas.load(_IP_KEY)


@types.registry.schemas(_IP_PRECISE_KEY)
def _get_ip_precise_schema():
    """ returns the schema for the ip.precise types """
    return schemas.load(_IP_PRECISE_KEY)


@types.registry.schemas(_NET_MAC_KEY)
def _get_mac_addr_schema():
    """ returns the schema for the net.mac types """
    return schemas.load(_NET_MAC_KEY)


@types.registry.types(_IPV4_KEY)
def _configure_ipv4(field_spec, _):
    """ configures value supplier for ipv4 type """
    return _configure_ip(field_spec, _)


@types.registry.types(_IP_KEY)
def _configure_ip(field_spec, loader):
    """ configures value supplier for ip type """
    config = utils.load_config(field_spec, loader)
    if 'base' in config and 'cidr' in config:
        raise SpecException('Must supply only one of base or cidr param: ' + json.dumps(field_spec))

    parts = _get_base_parts(config)
    # this is the same thing as a constant
    if len(parts) == 4:
        return suppliers.values('.'.join(parts))
    sample = config.get('sample', 'yes')
    octet_supplier_map = {
        'first': _create_octet_supplier(parts, 0, sample),
        'second': _create_octet_supplier(parts, 1, sample),
        'third': _create_octet_supplier(parts, 2, sample),
        'fourth': _create_octet_supplier(parts, 3, sample),
    }
    return ipv4(octet_supplier_map)


def _get_base_parts(config):
    """
    Builds the base ip array for the first N octets based on
    supplied base or on the /N subnet mask in the cidr
    """
    if 'base' in config:
        parts = config.get('base').split('.')
    else:
        parts = []

    if 'cidr' in config:
        cidr = config['cidr']
        if '/' in cidr:
            mask = cidr[cidr.index('/') + 1:]
            if not mask.isdigit():
                raise SpecException('Invalid Mask in cidr for config: ' + json.dumps(config))
            if int(mask) not in [8, 16, 24]:
                raise SpecException('Invalid Subnet Mask in cidr for config: ' + json.dumps(config)
                                            + ' only one of /8 /16 or /24 supported')
            ip_parts = cidr[0:cidr.index('/')].split('.')
            if len(ip_parts) < 4 or not all(part.isdigit() for part in ip_parts):
                raise SpecException('Invalid IP in cidr for config: ' + json.dumps(config))
            if mask == '8':
                parts = ip_parts[0:1]
            if mask == '16':
                parts = ip_parts[0:2]
            if mask == '24':
                parts = ip_parts[0:3]
        else:
            raise SpecException('Invalid Subnet Mask in cidr for config: ' + json.dumps(config)
                                + ' only one of /8 /16 or /24 supported')
    return parts


def _create_octet_supplier(parts, index, sample):
    """ creates a value supplier for the index'th octet """
    # this index is for a part that is static, create a single value supplier for that part
    if len(parts) >= index + 1 and parts[index].strip() != '':
        octet = parts[index].strip()
        if not octet.isdigit():
            raise SpecException(f'Octet: {octet} invalid for base, Invalid Input: ' + '.'.join(parts))
        if not 0 <= int(octet) <= 255:
            raise SpecException(
                f'Each octet: {octet} must be in range of 0 to 255, Invalid Input: ' + '.'.join(parts))
        return suppliers.values(octet)
    # need octet range at this point
    octet_range = list(range(0, 255))
    spec = {'config': {'sample': sample}, 'data': octet_range}
    return suppliers.values(spec)


@types.registry.types(_IP_PRECISE_KEY)
def _configure_precise_ip(field_spec, _):
    """ configures value supplier for ip.precise type """
    config = field_spec.get('config')
    if config is None:
        raise SpecException('No config for: ' + json.dumps(field_spec) + ', param cidr required')
    cidr = config.get('cidr')
    sample = config.get('sample', 'no').lower() in ['yes', 'true', 'on']
    if cidr is None:
        raise SpecException('Invalid config for: ' + json.dumps(field_spec) + ', param cidr required')
    return ip_precise(cidr, sample)


@types.registry.types(_NET_MAC_KEY)
def _configure_mac_address_supplier(field_spec, loader):
    """ configures value supplier for net.mac type """
    config = utils.load_config(field_spec, loader)
    if utils.is_affirmative('dashes', config):
        delim = '-'
    else:
        delim = types.get_default('mac_addr_separator')

    return mac_address(delim)
