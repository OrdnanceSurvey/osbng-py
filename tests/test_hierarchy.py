"""Testing for the hierarchy module.

The test cases are defined in the JSON file located at ./data/hierarchy_test_cases.json and are used to parameterise the tests for various functions in the indexing module.
Test cases are loaded from the JSON file using the _load_test_cases function, which is defined in the utils module.
The test cases are defined as TypedDicts, which provide a way to define the structure of the test case data.
"""

import pytest

from osbng.bng_reference import BNGReference
from osbng.errors import _EXCEPTION_MAP
from osbng.hierarchy import bng_to_children, bng_to_parent
from osbng.utils import _load_test_cases


# Parameterised test for bng_to_children function
@pytest.mark.parametrize(
    "test_case",
    # Load test cases from JSON file
    _load_test_cases(file_path="./data/hierarchy_test_cases.json")["bng_to_children"],
)
def test__bng_to_children(test_case):
    """Test bng_to_children with test cases from JSON file.

    Args:
        test_case (dict): Test case from JSON file.
    """
    # Load test case data
    bng_ref_string = test_case["bng_ref_string"]
    resolution = None if test_case["resolution"] == "NULL" else test_case["resolution"]
    # Get expected result
    expected = (
        None
        if "expected_exception" in test_case
        else test_case["expected"]["bng_ref_formatted"]
    )

    if "expected_exception" in test_case:
        # Get exception name from test case
        exception_name = test_case["expected_exception"]["name"]
        # Get exception message from test case
        message = (
            None
            if test_case["expected_exception"]["name"] == "BNGResolutionError"
            else test_case["expected_exception"]["message"]
        )
        # Get exception class from name
        exception_class = _EXCEPTION_MAP[exception_name]
        # Assert that the test case raises the expected exception and message
        with pytest.raises(exception_class, match=message):
            bng_to_children(BNGReference(bng_ref_string), resolution)

    else:
        # Return a list of child BNGReference objects
        bng_refs = bng_to_children(BNGReference(bng_ref_string), resolution)
        # Sort lists to account for order differences
        bng_ref_strings = [bng_ref.bng_ref_formatted for bng_ref in bng_refs]
        # Assert that the function returns the expected result
        assert sorted(bng_ref_strings) == sorted(expected)


# Parameterised test for bng_to_parent function
@pytest.mark.parametrize(
    "test_case",
    # Load test cases from JSON file
    _load_test_cases(file_path="./data/hierarchy_test_cases.json")["bng_to_parent"],
)
def test__bng_to_parent(test_case):
    """Test bng_to_parent with test cases from JSON file.

    Args:
        test_case (dict): Test case from JSON file.
    """
    # Load test case data
    bng_ref_string = test_case["bng_ref_string"]
    resolution = None if test_case["resolution"] == "NULL" else test_case["resolution"]

    if "expected_exception" in test_case:
        # Get exception name from test case
        exception_name = test_case["expected_exception"]["name"]
        # Get exception message from test case
        message = (
            None
            if test_case["expected_exception"]["name"] == "BNGResolutionError"
            else test_case["expected_exception"]["message"]
        )
        # Get exception class from name
        exception_class = _EXCEPTION_MAP[exception_name]
        # Assert that the test case raises the expected exception and message
        with pytest.raises(exception_class, match=message):
            bng_to_parent(BNGReference(bng_ref_string), resolution)

    else:
        # Return the parent BNGReference object
        bng_ref = bng_to_parent(BNGReference(bng_ref_string), resolution)
        # Assert that the function returns the expected result
        assert bng_ref.bng_ref_formatted == test_case["expected"]["bng_ref_formatted"]
