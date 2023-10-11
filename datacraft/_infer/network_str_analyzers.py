"""Looks for common network strings"""
import os
import re
from typing import List, Any, Dict

import datacraft
from datacraft import RefsAggregator
from .regex_str_analyzers import RegexStringAnalyzer

# Regular expression patterns for the network formats
IPV4_PATTERN = re.compile(
    r'^(25[0-5]|2[0-4]\d|[01]?\d\d?)\.(25[0-5]|2[0-4]\d|[01]?\d\d?)\.(25[0-5]|2[0-4]\d|[01]?\d\d?)\.(25[0-5]|2[0-4]\d|[01]?\d\d?)$')
MAC_ADDRESS_PATTERN = re.compile(r'^([\dA-Fa-f]{2}[:-]){5}([\dA-Fa-f]{2})$')

KEY_TO_PATTERN = {
    "ip": IPV4_PATTERN,
    "net.mac": MAC_ADDRESS_PATTERN
}


class IpAnalyzer(RegexStringAnalyzer):
    def generate_spec(self, name: str, values: List[Any], refs: RefsAggregator, **kwargs) -> Dict[str, Any]:
        result = super().generate_spec(name, values, refs, **kwargs)
        base = _longest_common_prefix(values)
        if len(base) > 0:
            result["config"] = {"base": base}
        return result


def _longest_common_prefix(ips):
    return os.path.commonprefix(ips).rpartition('.')[0]


@datacraft.registry.analyzers('network')
def _network_analyzer() -> datacraft.ValueListAnalyzer:
    return IpAnalyzer(KEY_TO_PATTERN)
