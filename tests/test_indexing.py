"""Testing for the indexing module.

Test cases are loaded from a JSON file using the _load_test_cases function from the utils module.
"""

import pytest

from osbng.indexing import (
    _validate_and_normalise_bng_resolution,
    _validate_easting_northing,
    _get_bng_suffix,
    xy_to_bng,
)
from osbng.errors import _EXCEPTION_MAP
from osbng.utils import _load_test_cases


# Parameterised test for _validate_and_normalise_bng_resolution function
@pytest.mark.parametrize(
    "test_case",
    _load_test_cases(file_path="./data/indexing_test_cases.json")[
        "_validate_and_normalise_bng_resolution"
    ],
)
def test__validate_and_normalise_bng_resolution(test_case):
    """Test _validate_and_normalise_bng_resolution with test cases from JSON file."""
    resolution = test_case["resolution"]
    if "expected_exception" in test_case:
        exception_name = test_case["expected_exception"]["name"]
        # Get exception class from name
        exception_class = _EXCEPTION_MAP[exception_name]
        with pytest.raises(exception_class):
            _validate_and_normalise_bng_resolution(resolution)
    else:
        assert (
            _validate_and_normalise_bng_resolution(resolution) == test_case["expected"]
        )


# Parameterised test for _validate_easting_northing function
@pytest.mark.parametrize(
    "test_case",
    _load_test_cases(file_path="./data/indexing_test_cases.json")[
        "_validate_easting_northing"
    ],
)
def test__validate_easting_northing(test_case):
    """Test _validate_and_normalise_bng_resolution with test cases from JSON file."""
    easting = test_case["easting"]
    northing = test_case["northing"]
    if "expected_exception" in test_case:
        exception_name = test_case["expected_exception"]["name"]
        # Get exception class from name
        exception_class = _EXCEPTION_MAP[exception_name]
        with pytest.raises(exception_class):
            _validate_easting_northing(easting, northing)
    else:
        _validate_easting_northing(easting, northing)


# Parameterised test for _get_bng_suffix function
@pytest.mark.parametrize(
    "test_case",
    _load_test_cases(file_path="./data/indexing_test_cases.json")["_get_bng_suffix"],
)
def test__get_bng_suffix(test_case):
    """Test _get_bng_suffix function with test cases from JSON file.

    Args:
        test_case (dict): Test case from JSON file.
    """
    easting = test_case["easting"]
    northing = test_case["northing"]
    resolution = test_case["resolution"]
    expected = test_case["expected"]
    assert _get_bng_suffix(easting, northing, resolution) == expected


# Parameterised test for xy_to_bng function
@pytest.mark.parametrize(
    "test_case",
    _load_test_cases(file_path="./data/indexing_test_cases.json")[
        "xy_to_bng"
    ],
)
def test_xy_to_bng(test_case):
    """Test xy_to_bng with test cases from JSON file."""
    easting = test_case["easting"]
    northing = test_case["northing"]
    resolution = test_case["resolution"]
    if "expected_exception" in test_case:
        exception_name = test_case["expected_exception"]["name"]
        # Get exception class from name
        exception_class = _EXCEPTION_MAP[exception_name]
        with pytest.raises(exception_class):
            xy_to_bng(easting, northing, resolution)
    else:
        bng = xy_to_bng(easting, northing, resolution)
        assert bng.bng_ref_formatted == test_case["expected"]["bng_ref_formatted"]
