""" init for datagen """

from .types import registry
from .model import DataSpec, Distribution, ValueSupplierInterface
from .casters import CasterInterface
from .loader import Loader, preprocess_spec
from .exceptions import SpecException, ResourceError
from .builder import spec_builder
from . import template_engines
from .supplier.core import *
from .defaults import *
from .preprocessor import *
from . import builder
from . import suppliers
from . import spec_formatters
from . import key_providers
from . import cli
from . import outputs
from . import server


def parse_spec(raw_spec: dict) -> DataSpec:
    """
    Parses the raw spec into a DataSpec object. Takes in specs that may contain shorthand specifications.

    Args:
        raw_spec: raw dictionary that conforms to JSON spec format

    Returns:
        the fully parsed and loaded spec
    """
    specs = preprocess_spec(raw_spec)
    return builder.DataSpecImpl(specs)
