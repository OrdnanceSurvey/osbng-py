"""Testing for the traversal module.

Test cases are loaded from a JSON file using the _load_test_cases function from the utils module.
"""

import pytest

from osbng.traversal import bng_distance, bng_is_neighbour
from osbng.errors import _EXCEPTION_MAP
from osbng.utils import _load_test_cases
from osbng.bng_reference import BNGReference


# Parameterised test for bng_distance function
@pytest.mark.parametrize(
    "test_case",
    _load_test_cases(file_path="./data/traversal_test_cases.json")["bng_distance"],
)
def test_bng_distance(test_case):
    """Test bng_distance with test cases from JSON file."""
    bng_ref1 = test_case["bng_ref_string_1"]
    bng_ref2 = test_case["bng_ref_string_2"]
    if "expected_exception" in test_case:
        exception_name = test_case["expected_exception"]["name"]
        # Get exception class from name
        exception_class = _EXCEPTION_MAP[exception_name]
        with pytest.raises(exception_class):
            bng_distance(BNGReference(bng_ref1), BNGReference(bng_ref2))
    else:
        distance = bng_distance(BNGReference(bng_ref1), BNGReference(bng_ref2))
        assert distance == test_case["expected"]


# Parameterised test for bng_is_neighbour function
@pytest.mark.parametrize(
    "test_case",
    _load_test_cases(file_path="./data/traversal_test_cases.json")["bng_is_neighbour"],
)
def test_bng_is_neighbour(test_case):
    """Test bng_is_neighbour with test cases from JSON file."""
    bng_ref1 = test_case["bng_ref_string_1"]
    bng_ref2 = test_case["bng_ref_string_2"]
    if "expected_exception" in test_case:
        exception_name = test_case["expected_exception"]["name"]
        message = (
            None
            if test_case["expected_exception"]["name"] == "BNGNeighbourError"
            else test_case["expected_exception"]["message"]
        )
        # Get exception class from name
        exception_class = _EXCEPTION_MAP[exception_name]
        with pytest.raises(exception_class, match=message):
            bng_is_neighbour(BNGReference(bng_ref1), BNGReference(bng_ref2))
    else:
        distance = bng_is_neighbour(BNGReference(bng_ref1), BNGReference(bng_ref2))
        assert distance == test_case["expected"]
