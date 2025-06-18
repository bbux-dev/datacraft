import pytest
import datacraft


def verify_decimal_precision(entries, max_precision):
    """Helper function to verify that all values have at most max_precision decimal places"""
    for entry in entries:
        value = entry["field"]
        str_value = str(value)
        if '.' in str_value:
            decimal_part = str_value.split('.')[1]
            assert len(decimal_part) <= max_precision, f"Value {value} has more than {max_precision} decimal places"


@pytest.mark.parametrize("precision", range(1, 8))
def test_number_precision_basic(precision):
    """Test number.N types produce at most N decimal places"""
    spec = {
        "field": {
            "type": f"number.{precision}",
            "data": [0, 10]
        }
    }

    entries = list(datacraft.entries(spec, 100))
    verify_decimal_precision(entries, precision)


@pytest.mark.parametrize("precision", range(1, 8))
def test_number_precision_negative_values(precision):
    """Test number.N types work with negative values"""
    spec = {
        "field": {
            "type": f"number.{precision}",
            "data": [-10, 10]
        }
    }

    entries = list(datacraft.entries(spec, 50))
    verify_decimal_precision(entries, precision)


@pytest.mark.parametrize("precision", range(1, 8))
def test_number_precision_large_range(precision):
    """Test number.N types work with large value ranges"""
    spec = {
        "field": {
            "type": f"number.{precision}",
            "data": [1000, 10000]
        }
    }

    entries = list(datacraft.entries(spec, 50))
    verify_decimal_precision(entries, precision)


@pytest.mark.parametrize("precision", range(1, 8))
def test_number_precision_small_range(precision):
    """Test number.N types work with small value ranges"""
    spec = {
        "field": {
            "type": f"number.{precision}",
            "data": [0, 1]
        }
    }

    entries = list(datacraft.entries(spec, 50))
    verify_decimal_precision(entries, precision)


@pytest.mark.parametrize("precision", range(1, 8))
def test_number_precision_nested_data(precision):
    """Test number.N types work with nested data arrays"""
    spec = {
        "field": {
            "type": f"number.{precision}",
            "data": [[0, 5], [5, 10]]
        }
    }

    entries = list(datacraft.entries(spec, 50))
    verify_decimal_precision(entries, precision)


@pytest.mark.parametrize("precision", range(1, 8))
def test_number_precision_with_config(precision):
    """Test number.N types work with additional config options"""
    spec = {
        "field": {
            "type": f"number.{precision}",
            "data": [0, 10],
            "config": {
                "precision": 8  # This should be overridden by the roundN cast
            }
        }
    }

    entries = list(datacraft.entries(spec, 50))
    verify_decimal_precision(entries, precision)


@pytest.mark.parametrize("precision", range(1, 8))
def test_number_precision_with_existing_cast(precision):
    """Test number.N types work when config already has cast options"""
    spec = {
        "field": {
            "type": f"number.{precision}",
            "data": [0, 10],
            "config": {
                "cast": "float"
            }
        }
    }

    entries = list(datacraft.entries(spec, 50))
    verify_decimal_precision(entries, precision)


@pytest.mark.parametrize("precision", range(1, 8))
def test_number_precision_edge_cases(precision):
    """Test number.N types with edge case values"""
    spec = {
        "field": {
            "type": f"number.{precision}",
            "data": [0, 0.1]  # Very small range
        }
    }

    entries = list(datacraft.entries(spec, 50))
    verify_decimal_precision(entries, precision)


@pytest.mark.parametrize("precision", range(1, 8))
def test_number_precision_zero_values(precision):
    """Test number.N types handle zero values correctly"""
    spec = {
        "field": {
            "type": f"number.{precision}",
            "data": [0, 0]  # Range of zero
        }
    }

    entries = list(datacraft.entries(spec, 10))
    verify_decimal_precision(entries, precision)


@pytest.mark.parametrize("invalid_precision", [0, 8, 9, 10])
def test_number_precision_invalid_types(invalid_precision):
    """Test that invalid number.N types raise appropriate errors"""
    with pytest.raises(datacraft.SpecException):
        spec = {
            "field": {
                "type": f"number.{invalid_precision}",
                "data": [0, 10]
            }
        }
        list(datacraft.entries(spec, 1))


def test_number_precision_verification():
    """Test that we can verify the actual decimal precision of generated values"""
    # Test with a known range that should produce various decimal places
    spec = {
        "field": {
            "type": "number.3",
            "data": [0, 1]  # Range 0-1 should produce values with decimals
        }
    }

    entries = list(datacraft.entries(spec, 100))

    # Verify we get some values with decimals
    has_decimals = False
    for entry in entries:
        value = entry["field"]
        str_value = str(value)
        if '.' in str_value:
            has_decimals = True

    # Verify precision constraint
    verify_decimal_precision(entries, 3)
    
    # At least some values should have decimals
    assert has_decimals, "Expected some values to have decimal places"
