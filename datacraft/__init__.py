""" init for datacraft """

import logging

# model classes that may be implemented externally
from .supplier.model import (
    DataSpec, ValueSupplierInterface, Distribution, CasterInterface, RecordProcessor, OutputHandlerInterface,
    ResettableIterator)
# programmatic spec building
from . import builder
# expose this at root too
from .builder import spec_builder, parse_spec
# registry decorators
from .registries import Registry as registry
# exceptions and errors thrown
from .exceptions import SpecException, ResourceError
from .supplier.exceptions import SupplierException
# commonly used by client code
from .loader import Loader
from . import suppliers, distributions, outputs
# to trigger registered functions
from . import cli

import importlib_metadata as metadata

_log = logging.getLogger('datacraft.init')


def _load_eps():
    """initiate any custom entry points"""
    eps = metadata.entry_points().get('datacraft.custom_type_loader', [])

    for ep in eps:
        plugin = ep.load()
        try:
            plugin()
        except Exception as err:
            _log.warning('Unable to initiate plugin: %s, error: %s', str(plugin), str(err))


_load_eps()
