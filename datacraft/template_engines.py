"""
Handles loading and creating the templating engine
"""
import os
from pathlib import Path
from typing import Union

from jinja2 import Environment, FileSystemLoader, BaseLoader, select_autoescape  # type: ignore

from .supplier.model import RecordProcessor


def for_file(template_file: Union[str, Path]) -> RecordProcessor:
    """
    Loads the templating engine for the template file specified

    Args:
        template_file: to fill in, string or Path

    Returns:
        the templating engine
    """
    return _Jinja2Engine(template_file)


def string(template: str) -> RecordProcessor:
    """ Returns a template engine for processing templates as strings """
    return _Jinja2StringEngine(template)


class _Jinja2Engine(RecordProcessor):
    """
    A simple class that creates a facade around a Jinja2 templating environment
    """

    def __init__(self, template_file: Union[str, Path]):
        template_dir = os.path.dirname(template_file)
        self.template_name = os.path.basename(template_file)
        env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )
        self.template = env.get_template(self.template_name)

    def process(self, record: Union[list, dict]) -> str:
        if isinstance(record, list):
            parts = [self.template.render(item) for item in record]
            return '\n'.join(parts)
        return self.template.render(record)


class _Jinja2StringEngine(RecordProcessor):
    """
    A Jinja2 Templating Engine for String Templates
    """

    def __init__(self, template_str):
        env = Environment(
            loader=BaseLoader(),
            autoescape=select_autoescape(['html', 'xml'])
        )
        self.template = env.from_string(template_str)

    def process(self, record: Union[list, dict]) -> str:
        """
        Render the template using the fields in the provided record

        Args:
            record: dictionary of field in template to value to populate the field with

        Returns:
            The rendered template
        """
        if isinstance(record, list):
            parts = [self.template.render(item) for item in record]
            return '\n'.join(parts)
        return self.template.render(record)
