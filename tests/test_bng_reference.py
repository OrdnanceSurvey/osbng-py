"""Testing for the bng_reference module.

Test cases are loaded from a JSON file using the load_test_cases function from the utils module.
"""

import pytest

from osbng.bng_reference import (
    _is_valid_bng,
    _get_bng_resolution,
    _get_bng_resolution_string,
    _get_bng_pretty_format,
)
from osbng.utils import load_test_cases


# Parameterised test for _is_valid_bng function
@pytest.mark.parametrize(
    "test_case",
    load_test_cases(file_path="./data/bng_reference_test_cases.json")["_is_valid_bng"],
)
def test__is_valid_bng(test_case):
    """Test _is_valid_bng function with test cases from JSON file.

    Args:
        test_case (dict): Test case from JSON file.
    """
    bng_ref_string = test_case["bng_ref_string"]
    expected = test_case["expected"]
    assert _is_valid_bng(bng_ref_string) == expected


# Parameterised test for _get_bng_resolution function
@pytest.mark.parametrize(
    "test_case",
    load_test_cases(file_path="./data/bng_reference_test_cases.json")[
        "_get_bng_resolution"
    ],
)
def test__get_bng_resolution(test_case):
    """Test _get_bng_resolution function with test cases from JSON file.

    Args:
        test_case (dict): Test case from JSON file.
    """
    bng_ref_string = test_case["bng_ref_string"]
    expected = test_case["expected"]
    assert _get_bng_resolution(bng_ref_string) == expected


# Parameterised test for _get_bng_resolution_string function
@pytest.mark.parametrize(
    "test_case",
    load_test_cases(file_path="./data/bng_reference_test_cases.json")[
        "_get_bng_resolution_string"
    ],
)
def test__get_bng_resolution_string(test_case):
    """Test _get_bng_resolution_string function with test cases from JSON file.

    Args:
        test_case (dict): Test case from JSON file.
    """
    bng_ref_string = test_case["bng_ref_string"]
    expected = test_case["expected"]
    assert _get_bng_resolution_string(bng_ref_string) == expected


# Parameterised test for _get_bng_pretty_format function
@pytest.mark.parametrize(
    "test_case",
    load_test_cases(file_path="./data/bng_reference_test_cases.json")[
        "_get_bng_pretty_format"
    ],
)
def test__get_bng_pretty_format(test_case):
    """Test _get_bng_pretty_format function with test cases from JSON file.

    Args:
        test_case (dict): Test case from JSON file.
    """
    bng_ref_string = test_case["bng_ref_string"]
    expected = test_case["expected"]
    assert _get_bng_pretty_format(bng_ref_string) == expected
