"""
Light weight module for running a Flask Server that returns data from a generator.
"""
from typing import Generator
import logging
import flask


_log = logging.getLogger(__name__)


class _Server:
    def __init__(self, generator, endpoint, data_is_json):
        self.generator = generator
        self.endpoint = endpoint
        self.data_is_json = data_is_json

    def callback(self):
        # next generated record
        try:
            data = next(self.generator)
        except StopIteration:
            _log.warning('No more iterations available')
            return flask.Response(None, status=204)
        if self.data_is_json:
            return flask.jsonify(data)
        return data

    def run(self):
        app = flask.Flask(__name__)
        _log.info('Adding endpoint to server: %s', self.endpoint)
        app.add_url_rule(self.endpoint, view_func=self.callback)
        app.run()


def run(generator: Generator, endpoint: str, data_is_json: bool):
    """
    Runs a light weight Flask server with data returned by the provided generator served at each subsequent call to
    the provided endpoint. End point should start with /. When StopIteration encountered, returns a 204 status code.

    Args:
        generator: that provides response data as dictionary
        endpoint: to serve data on i.e. /data
        data_is_json: if the data should be returned as JSON, default is as string
    """
    server = _Server(generator, endpoint, data_is_json)
    server.run()
    pass
