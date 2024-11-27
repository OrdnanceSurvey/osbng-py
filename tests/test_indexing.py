"""Testing for the indexing module.

Test cases are loaded from a JSON file using the load_test_cases function from the utils module.
"""

import pytest

from osbng.indexing import _validate_and_normalise_bng_resolution
from osbng.errors import BNGResolutionError
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
    expected = test_case["expected"]
    assert _validate_and_normalise_bng_resolution(resolution) == expected
