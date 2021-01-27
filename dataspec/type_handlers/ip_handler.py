import json
import random
import ipaddress
import dataspec
from dataspec import suppliers
from dataspec import SpecException


class IpV4Supplier:
    def __init__(self, cidr, sample):
        self.net = ipaddress.ip_network(cidr)
        self.sample = sample
        cnt = 0
        for _ in self.net:
            cnt += 1
        self.size = cnt

    def next(self, iteration):
        if self.sample:
            idx = random.randint(0, self.size-1)
        else:
            idx = iteration % self.size
        return str(self.net[idx])


class IpV4FastSupplier:
    def __init__(self, octet_supplier_map):
        self.octet_supplier_map = octet_supplier_map

    def next(self, iteration):
        first = self.octet_supplier_map['first'].next(iteration)
        second = self.octet_supplier_map['second'].next(iteration)
        third = self.octet_supplier_map['third'].next(iteration)
        fourth = self.octet_supplier_map['fourth'].next(iteration)
        return '.'.join(str(x) for x in [first, second, third, fourth])


@dataspec.registry.types('ip')
def configure_ip(field_spec, _):
    return _configure_supplier(field_spec)


@dataspec.registry.types('ipv4')
def configure_ipv4(field_spec, _):
    return _configure_supplier(field_spec)


@dataspec.registry.types('ip.fast')
def configure_ip(field_spec, _):
    config = field_spec.get('config', {})
    if 'base' in config:
        parts = config.get('base').split('.')
    else:
        parts = []

    # this is the same thing as a constant
    if len(parts) == 4:
        return suppliers.values(config.get('base'))

    sample = config.get('sample', 'yes')
    octet_supplier_map = {
        'first': _create_octet_supplier(parts, 0, sample),
        'second': _create_octet_supplier(parts, 1, sample),
        'third': _create_octet_supplier(parts, 2, sample),
        'fourth': _create_octet_supplier(parts, 3, sample),
    }
    return IpV4FastSupplier(octet_supplier_map)


def _create_octet_supplier(parts, index, sample):
    if len(parts) >= index + 1 and parts[index].strip() != '':
        octet = parts[index].strip()
        if not octet.isdigit():
            raise SpecException(f'Octet: {octet} invalid for base' + '.'.join(parts))
        return suppliers.values(octet)
    else:
        octet_range = list(range(0, 255))
        spec = {'config': {'sample': sample}, 'data': octet_range}
        return suppliers.values(spec)


def _configure_supplier(field_spec):
    config = field_spec.get('config')
    if config is None:
        raise SpecException('No config for: ' + json.dumps(field_spec) + ', param cidr required')
    cidr = config.get('cidr')
    sample = config.get('sample', 'no').lower() in ['yes', 'true', 'on']
    if cidr is None:
        raise SpecException('Invalid config for: ' + json.dumps(field_spec) + ', param cidr required')
    return IpV4Supplier(cidr, sample)
