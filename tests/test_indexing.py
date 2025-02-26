"""Testing for the indexing module.

Test cases are loaded from a JSON file using the _load_test_cases function from the utils module.
"""

import pytest

from osbng.bng_reference import BNGReference
from osbng.errors import _EXCEPTION_MAP
from osbng.indexing import (
    _validate_and_normalise_bng_resolution,
    _validate_easting_northing,
    _get_bng_suffix,
    xy_to_bng,
    bng_to_xy,
    bng_to_bbox
)
from osbng.utils import _load_test_cases


# Parameterised test for _validate_and_normalise_bng_resolution function
@pytest.mark.parametrize(
    "test_case",
    # Load test cases from JSON file
    _load_test_cases(file_path="./data/indexing_test_cases.json")[
        "_validate_and_normalise_bng_resolution"
    ],
)
def test__validate_and_normalise_bng_resolution(test_case):
    """Test _validate_and_normalise_bng_resolution with test cases from JSON file."""
    # Load test case data
    resolution = test_case["resolution"]

    # Check if the test case expects an exception
    if "expected_exception" in test_case:
        # Get exception name from test case
        exception_name = test_case["expected_exception"]["name"]
        # Get exception class from name
        exception_class = _EXCEPTION_MAP[exception_name]
        # Check that the function raises the expected exception
        with pytest.raises(exception_class):
            _validate_and_normalise_bng_resolution(resolution)
    else:
        # Get expected result
        expected = test_case["expected"]
        
        # Check that the function returns the expected result
        assert (
            _validate_and_normalise_bng_resolution(resolution) == expected
        )


# Parameterised test for _validate_easting_northing function
@pytest.mark.parametrize(
    "test_case",
    # Load test cases from JSON file
    _load_test_cases(file_path="./data/indexing_test_cases.json")[
        "_validate_easting_northing"
    ],
)
def test__validate_easting_northing(test_case):
    """Test _validate_and_normalise_bng_resolution with test cases from JSON file."""
    # Load test case data
    easting = test_case["easting"]
    northing = test_case["northing"]

    # Check if the test case expects an exception
    if "expected_exception" in test_case:
        # Get exception name from test case
        exception_name = test_case["expected_exception"]["name"]
        # Get exception class from name
        exception_class = _EXCEPTION_MAP[exception_name]
        # Check that the function raises the expected exception
        with pytest.raises(exception_class):
            _validate_easting_northing(easting, northing)
    else:
        # Check that the function does not raise any exception
        try:
            _validate_easting_northing(easting, northing)
        except Exception as e:
            pytest.fail(f"Unexpected exception raised: {e}")


# Parameterised test for _get_bng_suffix function
@pytest.mark.parametrize(
    "test_case",
    # Load test cases from JSON file
    _load_test_cases(file_path="./data/indexing_test_cases.json")["_get_bng_suffix"],
)
def test__get_bng_suffix(test_case):
    """Test _get_bng_suffix function with test cases from JSON file.

    Args:
        test_case (dict): Test case from JSON file.
    """
    # Load test case data
    easting = test_case["easting"]
    northing = test_case["northing"]
    resolution = test_case["resolution"]
    expected = test_case["expected"]

    # Check that the function returns the expected result
    assert _get_bng_suffix(easting, northing, resolution) == expected


# Parameterised test for xy_to_bng function
@pytest.mark.parametrize(
    "test_case",
    # Load test cases from JSON file
    _load_test_cases(file_path="./data/indexing_test_cases.json")["xy_to_bng"],
)
def test_xy_to_bng(test_case):
    """Test xy_to_bng with test cases from JSON file."""
    # Load test case data
    easting = test_case["easting"]
    northing = test_case["northing"]
    resolution = test_case["resolution"]

    # Check if the test case expects an exception
    if "expected_exception" in test_case:
        # Get exception name from test case
        exception_name = test_case["expected_exception"]["name"]
        # Get exception class from name
        exception_class = _EXCEPTION_MAP[exception_name]
        # Check that the function raises the expected exception
        with pytest.raises(exception_class):
            xy_to_bng(easting, northing, resolution)
    else:
        # Get expected result
        expected = test_case["expected"]["bng_ref_formatted"]

        # Create BNGReference object
        bng_ref = xy_to_bng(easting, northing, resolution)

        # Check that the function does not raise any exception
        assert bng_ref.bng_ref_formatted == expected


# Parameterised test for bng_to_xy function
@pytest.mark.parametrize(
    "test_case",
    # Load test cases from JSON file
    _load_test_cases(file_path="./data/indexing_test_cases.json")["bng_to_xy"],
)
def test_bng_to_xy(test_case):
    """Test bng_to_xy with test cases from JSON file."""
    # Load test case data
    bng_ref_string = test_case["bng_ref_string"]
    position = test_case["position"]
    # Get expected result as tuple
    expected = tuple(test_case["expected"])

    # Create BNGReference object
    bng_ref = BNGReference(bng_ref_string)

    # Assert that the function returns the expected result
    assert bng_to_xy(bng_ref, position) == expected


# Parameterised test for bng_to_bbox function
@pytest.mark.parametrize(
    "test_case",
    # Load test cases from JSON file
    _load_test_cases(file_path="./data/indexing_test_cases.json")["bng_to_bbox"],
)
def test_bng_to_bbox(test_case):
    """Test bng_to_bbox with test cases from JSON file."""
    # Load test case data
    bng_ref_string = test_case["bng_ref_string"]
    # Get expected result as tuple
    expected = tuple(test_case["expected"])

    # Create BNGReference object
    bng_ref = BNGReference(bng_ref_string)

    # Assert that the function returns the expected result
    assert bng_to_bbox(bng_ref) == expected
