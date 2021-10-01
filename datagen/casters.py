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
            if isinstance(value, list):
                return [float(val) for val in value]
            return float(value)
        except ValueError as err:
            raise SpecException(str(err))


class IntCaster(CasterInterface):
    def cast(self, value):
        try:
            if isinstance(value, list):
                return [int(float(val)) for val in value]
            return int(float(value))
        except ValueError as err:
            raise SpecException(str(err))


class StringCaster(CasterInterface):
    def cast(self, value):
        if isinstance(value, list):
            return [str(val) for val in value]
        return str(value)


class HexCaster(CasterInterface):
    def cast(self, value):
        if isinstance(value, list):
            return [hex(val) for val in value]
        return hex(value)


_CASTOR_MAP = {
    "i": IntCaster(),
    "int": IntCaster(),
    "f": FloatCaster(),
    "float": FloatCaster(),
    "s": StringCaster(),
    "str": StringCaster(),
    "string": StringCaster(),
    "h": HexCaster(),
    "hex": HexCaster()
}


def get(name):
    if name is None:
        return None
    return _CASTOR_MAP.get(name)
