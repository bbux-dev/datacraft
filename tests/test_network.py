import pytest

import datacraft

from . import builder

def test_ip_v4_spec():
    spec = _ipv4_spec(cidr="192.168.0.0/16")

    loader = datacraft.loader.field_loader(spec)
    supplier = loader.get('network')

    value = supplier.next(0)
    assert value.startswith('192.168.')

    value = supplier.next(256)
    assert value.startswith('192.168.')


def test_ip_precise_spec():
    spec = {
        "network:ip.precise?cidr=10.0.0.0/24": {}
    }

    loader = datacraft.loader.field_loader(spec)
    supplier = loader.get('network')

    value = supplier.next(0)
    assert value == '10.0.0.0'

    value = supplier.next(128)
    assert value == '10.0.0.128'

    # /24 means only last octet changes, so should roll over back to zero
    value = supplier.next(256)
    assert value == '10.0.0.0'


def test_ip_spec_precise_missing_config():
    spec = {"network:ip.precise": {}}
    _test_invalid_precise_spec(spec)


def test_ip_spec_precise_missing_cidr_param():
    spec = {"network:ip.precise": {"config": {"sample": "true"}}}
    _test_invalid_precise_spec(spec)


def _test_invalid_precise_spec(spec):
    loader = datacraft.loader.field_loader(spec)
    with pytest.raises(datacraft.SpecException):
        loader.get('network')


def test_ip_spec_invalid_base_and_cidr_specified():
    spec = {
        "network:ip?cidr=10.0.0.0/24&base=10.0.0": {}
    }
    loader = datacraft.loader.field_loader(spec)
    with pytest.raises(datacraft.SpecException):
        loader.get('network')


def test_ip_spec_unsupported_subnet_slice():
    _test_invalid_cidr('10.0.0.0/9')


def test_ip_spec_missing_subnet_slice():
    _test_invalid_cidr('10.0.0.0')


def test_ip_spec_cidr_ip_not_full():
    _test_invalid_cidr('10.0.0/16')


def test_ip_spec_cidr_ip_invalid_portion():
    _test_invalid_cidr('10.0.N.0/16')


def test_ip_spec_cidr_mask_not_number():
    _test_invalid_cidr('10.0.0.0/EIGHT')


def _test_invalid_cidr(cidr_value):
    spec = {
        f"network:ip?cidr={cidr_value}": {}
    }
    loader = datacraft.loader.field_loader(spec)
    with pytest.raises(datacraft.SpecException):
        loader.get('network')


def test_ip_spec_sample():
    spec = {
        "network": {
            "type": "ip",
            "config": {"cidr": "8.1.2.0/24", "sample": "true"}
        }
    }
    loader = datacraft.loader.field_loader(spec)
    supplier = loader.get('network')

    value = supplier.next(0)
    assert value is not None


def test_ip_spec_no_octets():
    loader = datacraft.loader.field_loader(_create_ip_spec_with_base('192.168.1.1'))
    supplier = loader.get('network')
    value = supplier.next(0)
    assert value == '192.168.1.1'


def test_ip_spec_three_octets():
    loader = datacraft.loader.field_loader(_create_ip_spec_with_base('10'))
    supplier = loader.get('network')
    value = supplier.next(0)
    assert value.startswith('10.')


def test_ip_spec_three_octets_dot_in_base():
    loader = datacraft.loader.field_loader(_create_ip_spec_with_base('11.'))
    supplier = loader.get('network')
    value = supplier.next(0)
    assert value.startswith('11.')
    assert not value.startswith('11..')


def test_ip_spec_invalid_base1():
    _test_ip_spec_invalid_base('INVALID.')


def test_ip_spec_invalid_base2():
    _test_ip_spec_invalid_base('1000.')


def test_default_delim_mac_address():
    spec = builder.spec_builder() \
        .add_field('mac', builder.mac()) \
        .build()
    value = next(spec.generator(1))['mac']
    assert len(value) == 17


def test_mac_address_dashes():
    spec_builder = builder.spec_builder()
    spec_builder.mac('mac', dashes='true')
    spec = spec_builder.build()
    value = next(spec.generator(1, enforce_schema=True))['mac']
    assert len(value) == 17
    assert '-' in value, f'No dashes in: {value}'


def _test_ip_spec_invalid_base(base):
    loader = datacraft.loader.field_loader(_create_ip_spec_with_base(base))
    with pytest.raises(datacraft.SpecException):
        loader.get('network')


def _create_ip_spec_with_base(base):
    return {
        "network": {
            "type": "ipv4",
            "config": {"base": base, "sample": "true"}
        }
    }


def _ip_spec(**config):
    return builder.spec_builder() \
        .add_field('network', builder.ip(**config)) \
        .build()


def _ipv4_spec(**config):
    return builder.spec_builder() \
        .add_field('network', builder.ipv4(**config)) \
        .build()


def _ip_precise_spec(**config):
    return builder.spec_builder() \
        .add_field('network', builder.ip_precise(**config)) \
        .build()
