"""
Module for network supplier implementations
"""
import ipaddress
import random
import string
from typing import Dict

from .model import ValueSupplierInterface


def ipv4(octet_supplier_map: Dict[str, ValueSupplierInterface]) -> ValueSupplierInterface:
    """
    Args:
        octet_supplier_map: dictionary mapping each octet to a ValueSupplier
    """
    return _IpV4Supplier(octet_supplier_map)


class _IpV4Supplier(ValueSupplierInterface):
    """
    Default implementation for generating ip values, uses separate suppliers for each octet of the ip
    """

    def __init__(self, octet_supplier_map: Dict[str, ValueSupplierInterface]):
        """
        Args:
            octet_supplier_map: dictionary mapping each octet to a ValueSupplier
        """
        self.first = octet_supplier_map['first']
        self.second = octet_supplier_map['second']
        self.third = octet_supplier_map['third']
        self.fourth = octet_supplier_map['fourth']

    def next(self, iteration):
        first = self.first.next(iteration)
        second = self.second.next(iteration)
        third = self.third.next(iteration)
        fourth = self.fourth.next(iteration)
        return f'{first}.{second}.{third}.{fourth}'


def ip_precise(cidr: str, sample: bool) -> ValueSupplierInterface:
    """
    Args:
        cidr: notation specifying ip range
        sample: if the ip addresses should be sampled from the available set
    """
    return _IpV4PreciseSupplier(cidr, sample)


class _IpV4PreciseSupplier(ValueSupplierInterface):
    """
    Class that supports precise ip address generation by specifying cidr values, much slower for large ip ranges
    """

    def __init__(self, cidr: str, sample: bool):
        """
        Args:
            cidr: notation specifying ip range
            sample: if the ip addresses should be sampled from the available set
        """
        self.net = ipaddress.ip_network(cidr)
        self.sample = sample
        cnt = 0
        for _ in self.net:
            cnt += 1
        self.size = cnt

    def next(self, iteration):
        if self.sample:
            idx = random.randint(0, self.size - 1)
        else:
            idx = iteration % self.size
        return str(self.net[idx])


def mac_address(delim: str) -> ValueSupplierInterface:
    """
    Args:
        delim: how mac address pieces are separated
    """
    return _MacAddressSupplier(delim)


class _MacAddressSupplier(ValueSupplierInterface):
    """ Class for supplying random mac addresses """
    def __init__(self, delim: str):
        """
        Args:
            delim: how mac address pieces are separated
        """
        self.delim = delim
        self.tokens = string.digits + 'ABCDEF'

    def next(self, iteration):
        parts = [''.join(random.sample(self.tokens, 2)) for _ in range(6)]
        return self.delim.join(parts)
