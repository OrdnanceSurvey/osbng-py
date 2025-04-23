"""Testing for the bng_reference module.

The test cases are defined in the JSON file located at ./data/bng_reference_test_cases.json and are used to parameterise the tests for various functions in the indexing module.
Test cases are loaded from the JSON file using the _load_test_cases function, which is defined in the utils module.
The test cases are defined as TypedDicts, which provide a way to define the structure of the test case data.
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
    # Load test cases from JSON file
    _load_test_cases(file_path="./data/bng_reference_test_cases.json")[
        "_validate_bng_ref_string"
    ],
)
def test__validate_bng_ref_string(test_case):
    """Test _validate_bng_ref_string function with test cases from JSON file.

    Args:
        test_case (dict): Test case from JSON file.
    """
    # Load test case data
    bng_ref_string = test_case["bng_ref_string"]
    expected = test_case["expected"]
    # Assert that the function returns the expected result
    assert _validate_bng_ref_string(bng_ref_string) == expected


# Parameterised test for _get_bng_resolution_metres function
@pytest.mark.parametrize(
    "test_case",
    # Load test cases from JSON file
    _load_test_cases(file_path="./data/bng_reference_test_cases.json")[
        "_get_bng_resolution_metres"
    ],
)
def test__get_bng_resolution_metres(test_case):
    """Test _get_bng_resolution_metres function with test cases from JSON file.

    Args:
        test_case (dict): Test case from JSON file.
    """
    # Load test case data
    bng_ref_string = test_case["bng_ref_string"]
    expected = test_case["expected"]
    # Assert that the function returns the expected result
    assert _get_bng_resolution_metres(bng_ref_string) == expected


# Parameterised test for _get_bng_resolution_label function
@pytest.mark.parametrize(
    "test_case",
    # Load test cases from JSON file
    _load_test_cases(file_path="./data/bng_reference_test_cases.json")[
        "_get_bng_resolution_label"
    ],
)
def test__get_bng_resolution_label(test_case):
    """Test _get_bng_resolution_label function with test cases from JSON file.

    Args:
        test_case (dict): Test case from JSON file.
    """
    # Load test case data
    bng_ref_string = test_case["bng_ref_string"]
    expected = test_case["expected"]
    # Assert that the function returns the expected result
    assert _get_bng_resolution_label(bng_ref_string) == expected


# Parameterised test for _format_bng_ref_string function
@pytest.mark.parametrize(
    "test_case",
    # Load test cases from JSON file
    _load_test_cases(file_path="./data/bng_reference_test_cases.json")[
        "_format_bng_ref_string"
    ],
)
def test__format_bng_ref_string(test_case):
    """Test _format_bng_ref_string function with test cases from JSON file.

    Args:
        test_case (dict): Test case from JSON file.
    """
    # Load test cases from JSON file
    bng_ref_string = test_case["bng_ref_string"]
    expected = test_case["expected"]
    # Assert that the function returns the expected result
    assert _format_bng_ref_string(bng_ref_string) == expected


# Parameterised test for BNGReference object
@pytest.mark.parametrize(
    "test_case",
    # Load test cases from JSON file
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
        # Get exception name from test case
        exception_name = test_case["expected_exception"]["name"]
        # Get exception class from name
        exception_class = _EXCEPTION_MAP[exception_name]
        # Assert that the test case raises the expected exception
        with pytest.raises(exception_class):
            BNGReference(test_case["bng_ref_string"])
    else:
        # Initialise BNGReference object with the test case input
        bng_ref = BNGReference(test_case["bng_ref_string"])

        # Assert that each property returns the expected value
        assert bng_ref.bng_ref_compact == test_case["expected_bng_ref_compact"]
        assert bng_ref.bng_ref_formatted == test_case["expected_bng_ref_formatted"]
        assert bng_ref.resolution_metres == test_case["expected_resolution_metres"]
        assert bng_ref.resolution_label == test_case["expected_resolution_label"]
