import pytest
from dataspec.loader import Loader
from dataspec import SpecException
# need this to trigger registration
from dataspec.type_handlers import ip_handler
import dataspec.preprocessor


def test_ip_v4_spec():
    spec = {
        "fooip": {
            "type": "ipv4",
            "config": {
                "cidr": "192.168.0.0/14"
            }
        }
    }

    loader = Loader(spec)
    supplier = loader.get('fooip')

    value = supplier.next(0)
    assert value == '192.168.0.0'

    value = supplier.next(256)
    assert value == '192.168.1.0'


def test_ip_spec():
    spec = {
        "network:ip?cidr=10.0.0.0/24": {}
    }

    loader = Loader(spec)
    supplier = loader.get('network')

    value = supplier.next(0)
    assert value == '10.0.0.0'

    value = supplier.next(128)
    assert value == '10.0.0.128'

    # /24 means only last octet changes, so should roll over back to zero
    value = supplier.next(256)
    assert value == '10.0.0.0'


def test_ip_spec_sample():
    spec = {
        "network": {
            "type": "ip",
            "config": {"cidr": "8.1.2.0/24", "sample": "true"}
        }
    }
    loader = Loader(spec)
    supplier = loader.get('network')

    value = supplier.next(0)
    assert value is not None


def test_ip_spec_fast_no_octets():
    loader = Loader(_create_fast_ip_spec('192.168.1.1'))
    supplier = loader.get('network')
    value = supplier.next(0)
    assert value == '192.168.1.1'


def test_ip_spec_fast_three_octets():
    loader = Loader(_create_fast_ip_spec('10'))
    supplier = loader.get('network')
    value = supplier.next(0)
    assert value.startswith('10.')


def test_ip_spec_fast_three_octets_dot_in_base():
    loader = Loader(_create_fast_ip_spec('11.'))
    supplier = loader.get('network')
    value = supplier.next(0)
    assert value.startswith('11.')
    assert not value.startswith('11..')


def test_ip_spec_fast_invalid_base():
    loader = Loader(_create_fast_ip_spec('INVALID.'))
    with pytest.raises(SpecException):
        loader.get('network')


def _create_fast_ip_spec(base):
    return {
        "network": {
            "type": "ip.fast",
            "config": {"base": base, "sample": "true"}
        }
    }

