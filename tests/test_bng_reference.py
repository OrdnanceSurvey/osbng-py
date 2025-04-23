"""Testing for the bng_reference module.

The test cases are defined in the JSON file located at ./data/bng_reference_test_cases.json and are used to parameterise the tests for various functions in the indexing module.
Test cases are loaded from the JSON file using the _load_test_cases function, which is defined in the utils module.
The test cases are defined as TypedDicts, which provide a way to define the structure of the test case data.
"""

from typing import TypedDict

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


class ValidateBNGRefStringTestCase(TypedDict):
    """TypedDict for _validate_bng_ref_string function test cases.

    Attributes:
        bng_ref_string (str): The BNG reference string to validate.
        expected (bool): True if the BNG reference is valid, False otherwise..
    """

    bng_ref_string: str
    expected: bool


# Parameterised test for _validate_bng_ref_string function
@pytest.mark.parametrize(
    "test_case",
    # Load test cases from JSON file
    _load_test_cases(file_path="./data/bng_reference_test_cases.json")[
        "_validate_bng_ref_string"
    ],
)
def test__validate_bng_ref_string(test_case: ValidateBNGRefStringTestCase):
    """Test _validate_bng_ref_string function with test cases from JSON file.

    Args:
        test_case (ValidateBNGRefStringTestCase): Test case from JSON file.
    """
    # Load test case data
    bng_ref_string = test_case["bng_ref_string"]
    expected = test_case["expected"]
    # Assert that the function returns the expected result
    assert _validate_bng_ref_string(bng_ref_string) == expected


class GetBNGResolutionMetresTestCase(TypedDict):
    """TypedDict for _get_bng_resolution_metres function test cases.

    Attributes:
        bng_ref_string (str): The BNG reference string to validate.
        expected (int): The resolution expressed as a metre-based integer.
    """

    bng_ref_string: str
    expected: int


# Parameterised test for _get_bng_resolution_metres function
@pytest.mark.parametrize(
    "test_case",
    # Load test cases from JSON file
    _load_test_cases(file_path="./data/bng_reference_test_cases.json")[
        "_get_bng_resolution_metres"
    ],
)
def test__get_bng_resolution_metres(test_case: GetBNGResolutionMetresTestCase):
    """Test _get_bng_resolution_metres function with test cases from JSON file.

    Args:
        test_case (GetBNGResolutionMetresTestCase): Test case from JSON file.
    """
    # Load test case data
    bng_ref_string = test_case["bng_ref_string"]
    expected = test_case["expected"]
    # Assert that the function returns the expected result
    assert _get_bng_resolution_metres(bng_ref_string) == expected


class GetBNGResolutionLabelTestCase(TypedDict):
    """TypedDict for _get_bng_resolution_label function test cases.

    Attributes:
        bng_ref_string (str): The BNG reference string to validate.
        expected (str): The resolution expressed as a descriptive string.
    """

    bng_ref_string: str
    expected: str


# Parameterised test for _get_bng_resolution_label function
@pytest.mark.parametrize(
    "test_case",
    # Load test cases from JSON file
    _load_test_cases(file_path="./data/bng_reference_test_cases.json")[
        "_get_bng_resolution_label"
    ],
)
def test__get_bng_resolution_label(test_case: GetBNGResolutionLabelTestCase):
    """Test _get_bng_resolution_label function with test cases from JSON file.

    Args:
        test_case (GetBNGResolutionLabelTestCase): Test case from JSON file.
    """
    # Load test case data
    bng_ref_string = test_case["bng_ref_string"]
    expected = test_case["expected"]
    # Assert that the function returns the expected result
    assert _get_bng_resolution_label(bng_ref_string) == expected


class FormatBNGRefStringTestCase(TypedDict):
    """TypedDict for _format_bng_ref_string function test cases.

    Attributes:
        bng_ref_string (str): The BNG reference string.
        expected (str): The pretty formatted BNG reference string.
    """

    bng_ref_string: str
    expected: str


# Parameterised test for _format_bng_ref_string function
@pytest.mark.parametrize(
    "test_case",
    # Load test cases from JSON file
    _load_test_cases(file_path="./data/bng_reference_test_cases.json")[
        "_format_bng_ref_string"
    ],
)
def test__format_bng_ref_string(test_case: FormatBNGRefStringTestCase):
    """Test _format_bng_ref_string function with test cases from JSON file.

    Args:
        test_case (FormatBNGRefStringTestCase): Test case from JSON file.
    """
    # Load test cases from JSON file
    bng_ref_string = test_case["bng_ref_string"]
    expected = test_case["expected"]
    # Assert that the function returns the expected result
    assert _format_bng_ref_string(bng_ref_string) == expected


class BNGReferenceTestCase(TypedDict):
    """TypedDict for _format_bng_ref_string function test cases.

    Attributes:
        bng_ref_string (str): The BNG reference string.
        expected_bng_ref_compact (str): The BNG reference with whitespace removed.
        expected_bng_ref_formatted (str): The pretty-formatted version of the BNG reference with single spaces between components.
        expected_resolution_metres (int): The resolution of the BNG reference in meters.
        expected_resolution_label (str): The resolution of the BNG reference expressed as a descriptive string.
    """

    bng_ref_string: str
    expected_bng_ref_compact: str
    expected_bng_ref_formatted: str
    expected_resolution_metres: int
    expected_resolution_label: str


# Parameterised test for BNGReference object
@pytest.mark.parametrize(
    "test_case",
    # Load test cases from JSON file
    _load_test_cases(file_path="./data/bng_reference_test_cases.json")["BNGReference"],
)
def test_bngreference(test_case: BNGReferenceTestCase):
    """Test BNGReference object with test cases from JSON file.

    Args:
        test_case (BNGReferenceTestCase): Test case from JSON file with the following keys:
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
