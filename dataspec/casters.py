"""
Module to handle casting of values to different types
"""
from .exceptions import SpecException


class CasterInterface:
    def cast(self, value):
        """ casts the value according to the specified type """


class FloatCaster(CasterInterface):
    def cast(self, value):
        try:
            return float(value)
        except ValueError as err:
            raise SpecException(str(err))


class IntCaster(CasterInterface):
    def cast(self, value):
        try:
            return int(float(value))
        except ValueError as err:
            raise SpecException(str(err))


class StringCaster(CasterInterface):
    def cast(self, value):
        return str(value)


_CASTOR_MAP = {
    "i": IntCaster(),
    "int": IntCaster(),
    "f": FloatCaster(),
    "float": FloatCaster(),
    "s": StringCaster(),
    "str": StringCaster(),
    "string": StringCaster()
}


def get(name):
    if name is None:
        return None
    return _CASTOR_MAP.get(name)
