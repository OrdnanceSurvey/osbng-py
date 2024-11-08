"""Testing for the bng_reference module.

Test cases are loaded from a JSON file using the load_test_cases function from the utils module.
"""

import pytest

from osbng.bng_reference import _is_valid_bng
from osbng.utils import load_test_cases


# Parameterised test for is_valid_bng function
@pytest.mark.parametrize(
    "test_case",
    load_test_cases(file_path="./data/bng_reference_test_cases.json")["_is_valid_bng"],
)
def test__is_valid_bng(test_case):
    """Test is_valid_bng function with test cases from JSON file.

    Args:
        test_case (dict): Test case from JSON file.
    """
    bng_ref_string = test_case["bng_ref_string"]
    expected = test_case["expected"]
    assert _is_valid_bng(bng_ref_string) == expected
