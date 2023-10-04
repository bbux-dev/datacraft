"""Looks for common date strings"""
import re

import datacraft
from .regex_str_analyzers import RegexStringAnalyzer

# Regular expression patterns for the date formats
DATE_PATTERN = re.compile(r'^\d{2}-\d{2}-\d{4}$')
DATE_ISO_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$')
DATE_ISO_MS_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}$')
DATE_ISO_US_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}$')

KEY_TO_PATTERN = {
    "date": DATE_PATTERN,
    "date.iso": DATE_ISO_PATTERN,
    "date.iso.ms": DATE_ISO_MS_PATTERN,
    "date.iso.us": DATE_ISO_US_PATTERN
}


@datacraft.registry.analyzers('date')
def _date_analyzer() -> datacraft.ValueListAnalyzer:
    return RegexStringAnalyzer(KEY_TO_PATTERN)
