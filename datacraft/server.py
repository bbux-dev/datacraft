"""
Light weight module for running a Flask Server that returns data from a generator.
"""
from typing import Generator
import logging
import flask

import datacraft

_log = logging.getLogger(__name__)


class _Server:
    """
    Light weight Flask server
    """

    def __init__(self,
                 generator: Generator,
                 endpoint: str,
                 data_is_json: bool,
                 count_supplier: datacraft.ValueSupplierInterface):
        self.generator = generator
        self.endpoint = endpoint
        self.data_is_json = data_is_json
        self.count_supplier = count_supplier
        self.call_number = 0

    def callback(self):
        """
        Callback for endpoint requests

        Returns:
            data as JSON or raw, until stop iteration, then 204 no more content
        """
        # next generated record
        num_records = self.count_supplier.next(self.call_number)
        try:
            data = [next(self.generator) for _ in range(num_records)]
        except StopIteration:
            _log.warning('No more iterations available')
            return flask.Response(None, status=204)
        if self.data_is_json:
            return flask.jsonify(data)
        # this may already be json or templated data
        if num_records == 1:
            return data[0]
        # cannot return list without jsonifying it
        return flask.jsonify(data)

    def run(self):
        """ run the Flask app """
        app = flask.Flask(__name__)
        _log.info('Adding endpoint to server: %s', self.endpoint)
        app.add_url_rule(self.endpoint, view_func=self.callback)
        app.run()


def run(generator: Generator,
        endpoint: str,
        data_is_json: bool,
        count_supplier: datacraft.ValueSupplierInterface):
    """
    Runs a light weight Flask server with data returned by the provided generator served at each subsequent call to
    the provided endpoint. End point should start with /. When StopIteration encountered, returns a 204 status code.

    Args:
        generator: that provides response data as dictionary
        endpoint: to serve data on i.e. /data
        data_is_json: if the data should be returned as JSON, default is as string
        count_supplier: supplies the number of values to generate for each call
    """
    server = _Server(generator, endpoint, data_is_json, count_supplier)
    server.run()
