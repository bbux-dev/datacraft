""" init for dataspec """
from .types import registry
from .loader import Loader, preprocess_spec
from .exceptions import SpecException, ResourceError
from .suppliers import ValueSupplierInterface

__version__ = '0.1.0'
