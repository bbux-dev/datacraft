"""
Module to handle casting of values to different types
"""
from typing import Any, Union, List
from abc import ABC, abstractmethod
from .exceptions import SpecException


class CasterInterface(ABC):
    """
    Interface for Classes that cast objects to different types
    """

    @abstractmethod
    def cast(self, value: Any) -> Any:
        """casts the value according to the specified type

        Args:
            value: to cast

        Returns:
            the cast form of the value

        Raises:
            SpecException when unable to cast value
        """


class FloatCaster(CasterInterface):
    """Casts values to floating point numbers if possible """

    def cast(self, value: Any) -> Union[float, List[float]]:
        try:
            if isinstance(value, list):
                return [float(val) for val in value]
            return float(value)
        except ValueError as err:
            raise SpecException from err


class IntCaster(CasterInterface):
    """Casts values to integers if possible """

    def cast(self, value: Any) -> Union[int, List[int]]:
        try:
            if isinstance(value, list):
                return [int(float(val)) for val in value]
            return int(float(value))
        except ValueError as err:
            raise SpecException from err


class StringCaster(CasterInterface):
    """Casts values to strings """

    def cast(self, value: Any) -> Union[str, List[str]]:
        if isinstance(value, list):
            return [str(val) for val in value]
        return str(value)


class HexCaster(CasterInterface):
    """Casts values to hexadecimal strings if possible """

    def cast(self, value: Any) -> Union[str, List[str]]:
        try:
            if isinstance(value, list):
                return [hex(int(float(val))) for val in value]
            return hex(int(float(value)))
        except ValueError as err:
            raise SpecException from err


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
    """Get the castor for the given name

    Args:
        name: of caster to get

    Returns:
        The caster for the name if one exists
    """
    if name is None:
        return None
    return _CASTOR_MAP.get(name)
