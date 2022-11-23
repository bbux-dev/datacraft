""" A tool for generating synthetic data.

Basic Usage:

>>> import datacraft
>>> spec = {
...     "id": {"type": "uuid"},
...     "timestamp": {"type": "date.iso.millis"},
...     "handle": {"type": "cc-word", "config": { "min": 4, "max": 8, "prefix": "@" } }
... }
>>> print(*datacraft.entries(spec, 3), sep='\\n')
{'id': '40bf8be1-23d2-4e93-9b8b-b37103c4b18c', 'timestamp': '2050-12-03T20:40:03.709', 'handle': '@WPNn'}
{'id': '3bb5789e-10d1-4ae3-ae61-e0682dad8ecf', 'timestamp': '2050-11-20T02:57:48.131', 'handle': '@kl1KUdtT'}
{'id': '474a439a-8582-46a2-84d6-58bfbfa10bca', 'timestamp': '2050-11-29T18:08:44.971', 'handle': '@XDvquPI'}

List all registered types:
>>> datacraft.registered_types()
['calculate', 'char_class', 'cc-ascii', 'cc-lower', '...', 'uuid', 'values', 'replace', 'regex_replace']

Print API usage for a specific type or types
>>> print(datacraft.type_usage('char_class', 'replace', '...'))
-------------------------------------
replace | API Example:

import datacraft

spec = {
  "field": {
    "type": "values",
    "data": ["foo", "bar", "baz"]
  },
  "replacement": {
    "type": "replace",
    "data": {"ba": "fi"},
    "ref": "field"
  }
}

print(*datacraft.entries(spec, 3), sep='\\n')

{'field': 'foo', 'replacement': 'foo'}
{'field': 'bar', 'replacement': 'fir'}
{'field': 'baz', 'replacement': 'fiz'}
"""

# model classes that may be implemented externally
from .supplier.model import (
    DataSpec, ValueSupplierInterface, Distribution, CasterInterface, RecordProcessor, OutputHandlerInterface,
    ResettableIterator, KeyProviderInterface)
# programmatic spec building
from . import builder
# expose this at root too
from .builder import parse_spec, entries, generator
# exceptions and errors thrown
from .exceptions import SpecException, ResourceError
from .supplier.exceptions import SupplierException
# commonly used by client code
from .loader import preprocess_spec, preprocess_and_format, Loader
from . import loader, suppliers, distributions, outputs, utils
from .usage import build_api_help as type_usage
from .usage import build_cli_help as cli_usage
# registry decorators
from .registries import Registry as registry
from .registries import registered_types, registered_formats, registered_casters
# to trigger registered functions
from . import cli
from . import entrypoints
entrypoints.load_eps()
