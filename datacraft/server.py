"""
Light weight module for running a Flask Server that returns data from a generator.
"""
import time
from typing import Generator, Union
import logging
import flask

import datacraft

_log = logging.getLogger(__name__)


class _Server:
    """
    Light weight Flask server
    """

    def __init__(self,
                 endpoint_specs: dict,
                 port: int,
                 host: str,
                 data_is_json: bool,
                 count_supplier: datacraft.ValueSupplierInterface,
                 delay: Union[float, None] = None):
        self.endpoint_specs = endpoint_specs
        self.port = port
        self.host = host
        self.data_is_json = data_is_json
        self.count_supplier = count_supplier
        self.delay = delay
        self.call_number = 0

    def generate_view_func(self, generator):
        """Generate a unique view function for a given endpoint configuration."""

        def view_func():
            """
            Callback for endpoint requests

            Returns:
                data as JSON or raw, until stop iteration, then 204 no more content
            """
            # next generated record
            num_records = self.count_supplier.next(self.call_number)
            try:
                data = [next(generator) for _ in range(num_records)]
            except StopIteration:
                _log.warning('No more iterations available')
                return flask.Response(None, status=204)
            if self.delay:
                time.sleep(self.delay)
            if self.data_is_json:
                return flask.jsonify(data)
            # this may already be json or templated data
            if num_records == 1:
                return data[0]
            # cannot return list without jsonifying it
            return flask.jsonify(data)

        return view_func

    def run(self):
        """ run the Flask app """
        app = flask.Flask(__name__)
        for endpoint_path, generator in self.endpoint_specs.items():
            _log.info('Adding endpoint to server: %s', endpoint_path)
            view_func = self.generate_view_func(generator)
            app.add_url_rule(endpoint_path,
                             endpoint=endpoint_path,
                             view_func=view_func,
                             methods=['POST', 'GET'])

        app.run(port=self.port, host=self.host)


def run(endpoint_map: dict,
        port: int,
        host: str,
        data_is_json: bool,
        count_supplier: datacraft.ValueSupplierInterface,
        delay: Union[float, None] = None):
    """
    Runs a light weight Flask server with data returned by the provided generator served at each subsequent call to
    the provided endpoint. End point should start with /. When StopIteration encountered, returns a 204 status code.

    Args:
        endpoint_map: endpoint to generator that provides response data as dictionary for that end point
        port: to serve data on e.g. 8080
        host: to list to traffic on e.g. localhost, 192.168.1.10
        data_is_json: if the data should be returned as JSON, default is as string
        count_supplier: supplies the number of values to generate for each call
        delay: number of seconds to pause between request and response
    """
    server = _Server(endpoint_map, port, host, data_is_json, count_supplier, delay)
    server.run()
