import json

import datagen


def test_server(mocker):
    mocker.patch('datagen.server.flask.Flask.run', return_value=None)

    spec = {"test:uuid": {}}

    gen = datagen.parse_spec(spec).generator(1)

    datagen.server.run(gen, endpoint='/test', data_is_json=True)


def test_server_callback_stop_iteration(mocker):
    mocker.patch('os._exit', return_value=None)
    mocker.patch('flask.jsonify', return_value=None)
    spec = {"test:uuid": {}}

    gen = datagen.parse_spec(spec).generator(1)

    server = datagen.server._Server(gen, endpoint='/test', data_is_json=True)

    # two calls should trigger the StopIteration
    server.callback()
    server.callback()


def test_server_callback(mocker):
    mocker.patch('sys.exit', return_value=None)
    spec = {"test:values": 42}

    processor = datagen.outputs.processor(format_name='json-pretty')
    gen = datagen.parse_spec(spec).generator(1, processor=processor)

    server = datagen.server._Server(gen, endpoint='/test', data_is_json=False)

    record = server.callback()
    assert record == json.dumps({'test': 42}, indent=4)
