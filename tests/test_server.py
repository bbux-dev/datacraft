import json

import datacraft


def test_server(mocker):
    mocker.patch('datacraft.server.flask.Flask.run', return_value=None)

    spec = {"test:uuid": {}}

    gen = datacraft.parse_spec(spec).generator(1)

    datacraft.server.run(gen, endpoint='/test', data_is_json=True)


def test_server_callback_stop_iteration(mocker):
    mocker.patch('flask.jsonify', return_value=None)
    spec = {"test:uuid": {}}

    gen = datacraft.parse_spec(spec).generator(1)

    server = datacraft.server._Server(gen, endpoint='/test', data_is_json=True)

    # two calls should trigger the StopIteration
    server.callback()
    server.callback()


def test_server_callback(mocker):
    spec = {"test:values": 42}

    processor = datacraft.outputs.processor(format_name='json-pretty')
    gen = datacraft.parse_spec(spec).generator(1, processor=processor)

    server = datacraft.server._Server(gen, endpoint='/test', data_is_json=False)

    record = server.callback()
    assert record == json.dumps({'test': 42}, indent=4)
