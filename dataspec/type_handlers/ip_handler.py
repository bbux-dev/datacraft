import json
import ipaddress
import dataspec
from dataspec import SpecException


class IpV4Supplier:
    def __init__(self, cidr):
        self.net = ipaddress.ip_network(cidr)
        cnt = 0
        for _ in self.net:
            cnt += 1
        self.size = cnt

    def next(self, iteration):
        idx = iteration % self.size
        return str(self.net[idx])


@dataspec.registry.types('ip')
def configure_ip(field_spec, _):
    return _configure_supplier(field_spec)


@dataspec.registry.types('ipv4')
def configure_ipv4(field_spec, _):
    return _configure_supplier(field_spec)


def _configure_supplier(field_spec):
    config = field_spec.get('config')
    if config is None:
        raise SpecException('No config for: ' + json.dumps(field_spec) + ', param cidr required')
    cidr = config.get('cidr')
    if cidr is None:
        raise SpecException('Invalid config for: ' + json.dumps(field_spec) + ', param cidr required')
    return IpV4Supplier(cidr)
