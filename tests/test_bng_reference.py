"""Testing for the bng_reference module.

Test cases are loaded from a JSON file using the _load_test_cases function from the utils module.
"""

import pytest

from osbng.bng_reference import (
    _validate_bng_ref_string,
    _get_bng_resolution_metres,
    _get_bng_resolution_label,
    _format_bng_ref_string,
    BNGReference,
)
from osbng.errors import _EXCEPTION_MAP
from osbng.utils import _load_test_cases


# Parameterised test for _validate_bng_ref_string function
@pytest.mark.parametrize(
    "test_case",
    _load_test_cases(file_path="./data/bng_reference_test_cases.json")["_validate_bng_ref_string"],
)
def test__validate_bng_ref_string(test_case):
    """Test _validate_bng_ref_string function with test cases from JSON file.

    Args:
        test_case (dict): Test case from JSON file.
    """
    bng_ref_string = test_case["bng_ref_string"]
    expected = test_case["expected"]
    assert _validate_bng_ref_string(bng_ref_string) == expected


# Parameterised test for _get_bng_resolution_metres function
@pytest.mark.parametrize(
    "test_case",
    _load_test_cases(file_path="./data/bng_reference_test_cases.json")[
        "_get_bng_resolution_metres"
    ],
)
def test__get_bng_resolution_metres(test_case):
    """Test _get_bng_resolution_metres function with test cases from JSON file.

    Args:
        test_case (dict): Test case from JSON file.
    """
    bng_ref_string = test_case["bng_ref_string"]
    expected = test_case["expected"]
    assert _get_bng_resolution_metres(bng_ref_string) == expected


# Parameterised test for _get_bng_resolution_label function
@pytest.mark.parametrize(
    "test_case",
    _load_test_cases(file_path="./data/bng_reference_test_cases.json")[
        "_get_bng_resolution_label"
    ],
)
def test__get_bng_resolution_label(test_case):
    """Test _get_bng_resolution_label function with test cases from JSON file.

    Args:
        test_case (dict): Test case from JSON file.
    """
    bng_ref_string = test_case["bng_ref_string"]
    expected = test_case["expected"]
    assert _get_bng_resolution_label(bng_ref_string) == expected


# Parameterised test for _format_bng_ref_string function
@pytest.mark.parametrize(
    "test_case",
    _load_test_cases(file_path="./data/bng_reference_test_cases.json")[
        "_format_bng_ref_string"
    ],
)
def test__format_bng_ref_string(test_case):
    """Test _format_bng_ref_string function with test cases from JSON file.

    Args:
        test_case (dict): Test case from JSON file.
    """
    bng_ref_string = test_case["bng_ref_string"]
    expected = test_case["expected"]
    assert _format_bng_ref_string(bng_ref_string) == expected


# Parameterised test for BNGReference object
@pytest.mark.parametrize(
    "test_case",
    _load_test_cases(file_path="./data/bng_reference_test_cases.json")["BNGReference"],
)
def test_bngreference(test_case):
    """Test BNGReference object with test cases from JSON file.

    Args:
        test_case (dict): Test case from JSON file with the following keys:
            - bng_ref_string
            - expected_bng_ref_compact
            - expected_bng_ref_formatted
            - expected_resolution_metres
            - expected_resolution_label
    """
    if "expected_exception" in test_case:
        exception_name = test_case["expected_exception"]["name"]
        # Get exception class from name
        exception_class = _EXCEPTION_MAP[exception_name]
        with pytest.raises(exception_class):
            BNGReference(test_case["bng_ref_string"])
    else:
        # Initialise BNGReference object with the test case input
        bng = BNGReference(test_case["bng_ref_string"])

        # Test each property against expected values
        assert bng.bng_ref_compact == test_case["expected_bng_ref_compact"]
        assert bng.bng_ref_formatted == test_case["expected_bng_ref_formatted"]
        assert bng.resolution_metres == test_case["expected_resolution_metres"]
        assert bng.resolution_label == test_case["expected_resolution_label"]
