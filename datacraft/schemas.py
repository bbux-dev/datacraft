"""
Module for validating schemas for various types
"""
import logging
from jsonschema import Draft7Validator  # type: ignore
from .exceptions import SpecException

_log = logging.getLogger(__name__)


def validate_schema_for_spec(spec_type: str, field_spec: dict, type_schema: dict):
    """
    performs schema validation for the provided field_spec

    Args:
        spec_type: type name for spec
        field_spec: spec to apply validation to
        type_schema: schema to use for validation

    Raises:
        SpecException if validation fails
    """
    validator = Draft7Validator(type_schema)
    errors = sorted(validator.iter_errors(field_spec), key=lambda e: e.path)
    if len(errors) > 0:
        for error in errors:
            _log.warning(error.message)
        raise SpecException(f'Failed to validate spec type: {spec_type} with spec: {field_spec}')
