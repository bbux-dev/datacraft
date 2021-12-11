"""
Module for datacraft exceptions
"""


class SpecException(Exception):
    """
    A SpecException indicates that there is a fatal flaw with the configuration or data associated with a Data Spec or
    one of the described Field Specs. Common errors include undefined or misspelled references, missing or invalid
    configuration parameters, and invalid or missing data definitions.
    """


class ResourceError(Exception):
    """
    A ResourceLoadError indicates that an underlying resource such as a schema file was not able to be found or loaded.
    """
