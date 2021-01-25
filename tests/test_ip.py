import re
from dataspec.loader import Loader
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
