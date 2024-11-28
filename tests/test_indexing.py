"""Testing for the indexing module.

Test cases are loaded from a JSON file using the load_test_cases function from the utils module.
"""

import pytest

from osbng.indexing import (
    _validate_and_normalise_bng_resolution,
    _validate_easting_northing,
)
from osbng.errors import BNGResolutionError, EXCEPTION_MAP
from osbng.utils import load_test_cases


# Parameterised test for _validate_and_normalise_bng_resolution function
@pytest.mark.parametrize(
    "test_case",
    load_test_cases(file_path="./data/indexing_test_cases.json")[
        "_validate_and_normalise_bng_resolution"
    ],
)
def test__validate_and_normalise_bng_resolution(test_case):
    """Test _validate_and_normalise_bng_resolution with test cases from JSON file."""
    resolution = test_case["resolution"]
    if "expected_exception" in test_case:
        exception_name = test_case["expected_exception"]["name"]
        # Get exception class from name
        exception_class = EXCEPTION_MAP[exception_name]
        with pytest.raises(exception_class):
            _validate_and_normalise_bng_resolution(resolution)
    else:
        assert (
            _validate_and_normalise_bng_resolution(resolution) == test_case["expected"]
        )


# Parameterised test for _validate_easting_northing function
@pytest.mark.parametrize(
    "test_case",
    load_test_cases(file_path="./data/indexing_test_cases.json")[
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
        exception_class = EXCEPTION_MAP[exception_name]
        with pytest.raises(exception_class):
            _validate_easting_northing(easting, northing)
    else:
        _validate_easting_northing(easting, northing)
