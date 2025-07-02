"""Testing for the traversal module.

The test cases are defined in the JSON file located at ./data/traversal_test_cases.json and are used to parameterise the tests for various functions in the traversal module.
Test cases are loaded from the JSON file using the _load_test_cases function, which is defined in the utils module.
The test cases are defined as TypedDicts, which provide a way to define the structure of the test case data.
"""

import pytest

from osbng.bng_reference import BNGReference
from osbng.errors import _EXCEPTION_MAP
from osbng.traversal import *
from osbng.utils import _load_test_cases


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
    elif "edge_to_edge" in test_case:
        edge_to_edge = test_case["edge_to_edge"]
        distance = bng_distance(BNGReference(bng_ref1), BNGReference(bng_ref2), edge_to_edge=edge_to_edge)
        assert distance == test_case["expected"]
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


# Parameterised test for bng_kring function
@pytest.mark.parametrize(
    "test_case",
    _load_test_cases(file_path="./data/traversal_test_cases.json")["bng_kring"],
)
def test_bng_kring(test_case):
    """Test bng_kring with test cases from JSON file."""

    if "expected_length" in test_case:
        assert len(bng_kring(BNGReference(test_case["bng_ref_string"]), test_case["k"])) == test_case["expected_length"]
    else:
        kring = bng_kring(BNGReference(test_case["bng_ref_string"]), test_case["k"])
        assert sorted([r.bng_ref_formatted for r in kring]) == sorted(test_case["expected"]["bng_ref_formatted"])


# Parameterised test for bng_kdisc function
@pytest.mark.parametrize(
    "test_case",
    _load_test_cases(file_path="./data/traversal_test_cases.json")["bng_kdisc"],
)
def test_bng_kdisc(test_case):
    """Test bng_kdisc with test cases from JSON file."""

    if "expected_length" in test_case:
        assert len(bng_kdisc(BNGReference(test_case["bng_ref_string"]), test_case["k"])) == test_case["expected_length"]
    else:
        kring = bng_kdisc(BNGReference(test_case["bng_ref_string"]), test_case["k"])
        assert sorted([r.bng_ref_formatted for r in kring]) == sorted(test_case["expected"]["bng_ref_formatted"])


# Parameterised test for bng_dwithin function
@pytest.mark.parametrize(
    "test_case",
    _load_test_cases(file_path="./data/traversal_test_cases.json")["bng_dwithin"],
)
def test_bng_dwithin(test_case):
    """Test bng_dwithin with test cases from JSON file."""

    if "expected_length" in test_case:
        assert len(bng_dwithin(BNGReference(test_case["bng_ref_string"]), test_case["d"])) == test_case["expected_length"]
    else:
        kring = bng_dwithin(BNGReference(test_case["bng_ref_string"]), test_case["d"])
        assert sorted([r.bng_ref_formatted for r in kring]) == sorted(test_case["expected"]["bng_ref_formatted"])

