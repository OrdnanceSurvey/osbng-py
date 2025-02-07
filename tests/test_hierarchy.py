"""Testing for the hierarchy module.

Test cases are loaded from a JSON file using the load_test_cases function from the utils module.
"""

import pytest

from osbng.hierarchy import bng_to_children, bng_to_parent
from osbng.bng_reference import BNGReference
from osbng.errors import _EXCEPTION_MAP
from osbng.utils import _load_test_cases


@pytest.mark.parametrize(
    "test_case",
    _load_test_cases(file_path="./data/hierarchy_test_cases.json")["bng_to_children"],
)
def test__bng_to_children(test_case):
    """Test bng_to_children with test cases from JSON file.

    Args:
        test_case (dict): Test case from JSON file.
    """
    bng_ref_string = test_case["bng_ref_string"]
    resolution = None if test_case["resolution"] == "NULL" else test_case["resolution"]

    if "expected_exception" in test_case:
        exception_name = test_case["expected_exception"]["name"]
        message = (
            None
            if test_case["expected_exception"]["name"] == "BNGResolutionError"
            else test_case["expected_exception"]["message"]
        )
        # Get exception class from name
        exception_class = _EXCEPTION_MAP[exception_name]
        with pytest.raises(exception_class, match=message):
            bng_to_children(BNGReference(bng_ref_string), resolution)

    else:

        bng_refs = bng_to_children(BNGReference(bng_ref_string), resolution)

        for bng_ref, expected in zip(bng_refs, test_case["expected"]):
            assert bng_ref.bng_ref_formatted == expected["bng_ref_formatted"]


@pytest.mark.parametrize(
    "test_case",
    _load_test_cases(file_path="./data/hierarchy_test_cases.json")["bng_to_parent"],
)
def test__bng_to_parent(test_case):
    """Test bng_to_parent with test cases from JSON file.

    Args:
        test_case (dict): Test case from JSON file.
    """
    bng_ref_string = test_case["bng_ref_string"]
    resolution = None if test_case["resolution"] == "NULL" else test_case["resolution"]

    if "expected_exception" in test_case:
        exception_name = test_case["expected_exception"]["name"]
        message = (
            None
            if test_case["expected_exception"]["name"] == "BNGResolutionError"
            else test_case["expected_exception"]["message"]
        )

        # Get exception class from name
        exception_class = _EXCEPTION_MAP[exception_name]
        with pytest.raises(exception_class, match=message):
            bng_to_parent(BNGReference(bng_ref_string), resolution)

    else:

        bng_ref = bng_to_parent(BNGReference(bng_ref_string), resolution)
        assert bng_ref.bng_ref_formatted == test_case["expected"]["bng_ref_formatted"]
