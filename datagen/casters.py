"""
Module to handle casting of values to different types
"""
from typing import Any, Union, List

from . import types
from .exceptions import SpecException
from .supplier.model import CasterInterface


class _FloatCaster(CasterInterface):
    """
    Casts values to floating point numbers if possible """

    def cast(self, value: Any) -> Union[float, List[float]]:
        try:
            if isinstance(value, list):
                return [float(val) for val in value]
            return float(value)
        except ValueError as err:
            raise SpecException from err


class _IntCaster(CasterInterface):
    """Casts values to integers if possible """

    def cast(self, value: Any) -> Union[int, List[int]]:
        try:
            if isinstance(value, list):
                return [int(float(val)) for val in value]
            return int(float(value))
        except ValueError as err:
            raise SpecException from err


class _StringCaster(CasterInterface):
    """Casts values to strings """

    def cast(self, value: Any) -> Union[str, List[str]]:
        if isinstance(value, list):
            return [str(val) for val in value]
        return str(value)


class _HexCaster(CasterInterface):
    """Casts values to hexadecimal strings if possible """

    def cast(self, value: Any) -> Union[str, List[str]]:
        try:
            if isinstance(value, list):
                return [hex(int(float(val))) for val in value]
            return hex(int(float(value)))
        except ValueError as err:
            raise SpecException from err


class _LowerCaster(CasterInterface):
    """Lower cases values as strings """

    def cast(self, value: Any) -> Union[str, List[str]]:
        if isinstance(value, list):
            return [str(val).lower() for val in value]
        return str(value).lower()


class _UpperCaster(CasterInterface):
    """Upper cases values as strings """

    def cast(self, value: Any) -> Union[str, List[str]]:
        if isinstance(value, list):
            return [str(val).upper() for val in value]
        return str(value).upper()


class _TrimCaster(CasterInterface):
    """Trims leading and trailing whitespace from values as strings """

    def cast(self, value: Any) -> Union[str, List[str]]:
        if isinstance(value, list):
            return [str(val).strip() for val in value]
        return str(value).strip()


class _RoundCaster(CasterInterface):
    """ Rounds value to specific number of digits """

    def __init__(self, digits):
        self.digits = digits

    def cast(self, value: Any) -> Union[int, float, List[int], List[float]]:
        if isinstance(value, list):
            return [self._round(val) for val in value]
        return self._round(value)

    def _round(self, value):
        if self.digits is None:
            return round(float(value))
        return round(float(value), self.digits)


class _MultiCaster(CasterInterface):
    """ Apply multiple casters in order """

    def __init__(self, casters: List[CasterInterface]):
        self.casters = casters

    def cast(self, value: Any) -> Any:
        for caster in self.casters:
            value = caster.cast(value)
        return value


_CASTER_MAP = {
    "i": _IntCaster(),
    "int": _IntCaster(),
    "f": _FloatCaster(),
    "float": _FloatCaster(),
    "s": _StringCaster(),
    "str": _StringCaster(),
    "string": _StringCaster(),
    "h": _HexCaster(),
    "hex": _HexCaster(),
    "l": _LowerCaster(),
    "lower": _LowerCaster(),
    "u": _UpperCaster(),
    "upper": _UpperCaster(),
    "t": _TrimCaster(),
    "trim": _TrimCaster(),
    "round": _RoundCaster(None)
}
for i in range(8):
    _CASTER_MAP[f'round{i}'] = _RoundCaster(i)


def get(name):
    """
    Get the caster for the given name

    Args:
        name: of caster to get

    Returns:
        The caster for the name if one exists
    """
    if name is None:
        return None
    names = name.split(";")
    casters = [_lookup_name(caster_name) for caster_name in names]
    if any(caster is None for caster in casters):
        raise SpecException('Unknown caster name in: ' + name)
    if len(casters) == 1:
        return casters[0]
    return _MultiCaster(casters)


def from_config(config: dict):
    """ returns the caster object from the config """
    return get(config.get('cast'))


def _lookup_name(name):
    if name in _CASTER_MAP:
        return _CASTER_MAP.get(name)
    # check registry
    return types.lookup_caster(name)
