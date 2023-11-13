import json

import pytest

import datacraft


@pytest.fixture()
def one():
    return datacraft.suppliers.count_supplier(data=1)


def test_server(mocker, one):
    mocker.patch('datacraft.server.flask.Flask.run', return_value=None)

    spec = {"test:uuid": {}}

    gen = datacraft.parse_spec(spec).generator(1)

    datacraft.server.run({'/test': gen}, port=None, data_is_json=True, count_supplier=one)


def test_server_callback_stop_iteration(mocker, one):
    mocker.patch('flask.jsonify', return_value=None)
    spec = {"test:uuid": {}}

    gen = datacraft.parse_spec(spec).generator(1)

    server = datacraft.server._Server({'/test': gen}, port=None, data_is_json=True, count_supplier=one)
    callback = server.generate_view_func(gen)
    # two calls should trigger the StopIteration
    callback()
    callback()


def test_server_callback(mocker, one):
    spec = {"test:values": 42}

    processor = datacraft.outputs.processor(format_name='json-pretty')
    gen = datacraft.parse_spec(spec).generator(1, processor=processor)

    server = datacraft.server._Server({'/test': gen}, port=None, data_is_json=False, count_supplier=one)
    callback = server.generate_view_func(gen)

    record = callback()
    assert record == json.dumps({'test': 42}, indent=4)
