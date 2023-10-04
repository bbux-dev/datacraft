"""Looks for common network strings"""
import re

import datacraft
from .regex_str_analyzers import RegexStringAnalyzer

# Regular expression patterns for the network formats
IPV4_PATTERN = re.compile(r'^(25[0-5]|2[0-4]\d|[01]?\d\d?)\.(25[0-5]|2[0-4]\d|[01]?\d\d?)\.(25[0-5]|2[0-4]\d|[01]?\d\d?)\.(25[0-5]|2[0-4]\d|[01]?\d\d?)$')
MAC_ADDRESS_PATTERN = re.compile(r'^([\dA-Fa-f]{2}[:-]){5}([\dA-Fa-f]{2})$')

KEY_TO_PATTERN = {
    "ip": IPV4_PATTERN,
    "net.mac": MAC_ADDRESS_PATTERN
}


@datacraft.registry.analyzers('network')
def _network_analyzer() -> datacraft.ValueListAnalyzer:
    return RegexStringAnalyzer(KEY_TO_PATTERN)
