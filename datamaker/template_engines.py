"""
Handles loading and creating the templating engine
"""
import os
from jinja2 import Environment, FileSystemLoader, select_autoescape


def load(template_file):
    """
    Loads the templating engine for the template file specified
    :param template_file: to fill in
    :return: the templating engine
    """
    return Jinja2Engine(template_file)


class Jinja2Engine:
    """
    A simple class that creates a facade around a Jinja2 templating environment
    """

    def __init__(self, template_file):
        template_dir = os.path.dirname(template_file)
        self.template_name = os.path.basename(template_file)
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )

    def process(self, record):
        """
        Render the template using the fields in the provided record
        :param record: dictionary of field in template to value to populate the field with
        :return: The rendered template
        """
        template = self.env.get_template(self.template_name)
        return template.render(record)
