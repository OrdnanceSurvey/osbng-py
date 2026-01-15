"""Testing for the traversal module.

The test cases are defined in the JSON file located at ./data/traversal_test_cases.json
and are used to parameterise the tests for various functions in the traversal module.
Test cases are loaded from the JSON file using the _load_test_cases function, which is
defined in the utils module. The test cases are defined as TypedDicts, which provide a
way to define the structure of the test case data.
"""

from pathlib import Path
from typing import TypedDict

import pytest

from osbng.bng_reference import BNGReference
from osbng.errors import _EXCEPTION_MAP
from osbng.traversal import (
    bng_distance,
    bng_dwithin,
    bng_is_neighbour,
    bng_kdisc,
    bng_kring,
)
from osbng.utils import _load_test_cases


class BNGDistanceTestCase(TypedDict):
    """TypedDict for bng_distance function test cases.

    Attributes:
        bng_ref_string_1 (str): The first BNG reference string.
        bng_ref_string_2 (str): The second BNG reference string.
        edge_to_edge (bool | None): Whether to calculate edge-to-edge distance.
        expected (float): The expected distance between the pair of BNGReference
            objects.
    """

    bng_ref_string_1: str
    bng_ref_string_2: str
    edge_to_edge: bool | None
    expected: float


# Parameterised test for bng_distance function
@pytest.mark.parametrize(
    "test_case",
    # Load test cases from JSON file
    _load_test_cases(
        file_path=Path(__file__).parent / "data" / "traversal_test_cases.json"
    )["bng_distance"],
)
def test_bng_distance(test_case: BNGDistanceTestCase) -> None:
    """Test bng_distance with test cases from JSON file.

    Args:
        test_case (BNGDistanceTestCase): The test case from JSON file.
    """
    # Load test case data
    bng_ref1 = test_case["bng_ref_string_1"]
    bng_ref2 = test_case["bng_ref_string_2"]

    if "expected_exception" in test_case:
        # Get exception name from test case
        exception_name = test_case["expected_exception"]["name"]
        # Get exception class from name
        exception_class = _EXCEPTION_MAP[exception_name]
        # Assert that the test case raises the expected exception
        with pytest.raises(exception_class):
            bng_distance(BNGReference(bng_ref1), BNGReference(bng_ref2))

    elif "edge_to_edge" in test_case:
        # If edge_to_edge is specified, use it in the distance calculation
        edge_to_edge = test_case["edge_to_edge"]
        # Assert that the function returns the expected result
        distance = bng_distance(
            BNGReference(bng_ref1), BNGReference(bng_ref2), edge_to_edge=edge_to_edge
        )
        assert distance == test_case["expected"]

    else:
        # Assert that the function returns the expected result
        distance = bng_distance(BNGReference(bng_ref1), BNGReference(bng_ref2))
        assert distance == test_case["expected"]


class BNGIsNeighbourTestCase(TypedDict):
    """TypedDict for bng_is_neighbour function test cases.

    Attributes:
        bng_ref_string_1 (str): The first BNG reference string.
        bng_ref_string_2 (str): The second BNG reference string.
        expected_exception (dict[str, str] | None): The expected exception is a
            dictionary with the exception name and message.
        expected (bool | None): The expected result of the neighbour check.
    """

    bng_ref_string_1: str
    bng_ref_string_2: str
    expected_exception: dict[str, str] | None
    expected: bool | None


# Parameterised test for bng_is_neighbour function
@pytest.mark.parametrize(
    "test_case",
    # Load test cases from JSON file
    _load_test_cases(
        file_path=Path(__file__).parent / "data" / "traversal_test_cases.json"
    )["bng_is_neighbour"],
)
def test_bng_is_neighbour(test_case: BNGIsNeighbourTestCase) -> None:
    """Test bng_is_neighbour with test cases from JSON file.

    Args:
        test_case (BNGIsNeighbourTestCase): The test case from JSON file.
    """
    # Load test case data
    bng_ref1 = test_case["bng_ref_string_1"]
    bng_ref2 = test_case["bng_ref_string_2"]

    if "expected_exception" in test_case:
        # Get exception name from test case
        exception_name = test_case["expected_exception"]["name"]
        # Get exception message from test case
        message = (
            None
            if test_case["expected_exception"]["name"] == "BNGNeighbourError"
            else test_case["expected_exception"]["message"]
        )
        # Get exception class from name
        exception_class = _EXCEPTION_MAP[exception_name]
        # Assert that the test case raises the expected exception
        with pytest.raises(exception_class, match=message):
            bng_is_neighbour(BNGReference(bng_ref1), BNGReference(bng_ref2))

    else:
        # Assert that the function returns the expected result
        distance = bng_is_neighbour(BNGReference(bng_ref1), BNGReference(bng_ref2))
        assert distance == test_case["expected"]


class BNGKRingTestCase(TypedDict):
    """TypedDict for bng_kring function test cases.

    Attributes:
        bng_ref_string (str): The BNG reference string.
        k (int): The k value for the k-ring.
        expected_warning (bool | None): The expected warning is a boolean indicating if
            a warning is expected.
        expected (dict[str, list[str]] | None): The expected result is a dictionary with
            the key "bng_ref_formatted" and a list of formatted BNG reference strings.
        expected_length (int | None): The expected length of the k-ring. Represents the
            number of BNGReference objects within k-ring.
    """

    bng_ref_string: str
    k: int
    expected_warning: bool | None
    expected: dict[str, list[str]] | None
    expected_length: int | None


# Parameterised test for bng_kring function
@pytest.mark.parametrize(
    "test_case",
    # Load test cases from JSON file
    _load_test_cases(
        file_path=Path(__file__).parent / "data" / "traversal_test_cases.json"
    )["bng_kring"],
)
def test_bng_kring(test_case: BNGKRingTestCase) -> None:
    """Test bng_kring with test cases from JSON file.

    Args:
        test_case (BNGKRingTestCase): The test case from JSON file.
    """
    # Load test case data
    bng_ref_string = test_case["bng_ref_string"]
    k = test_case["k"]
    # Get expected result
    expected = (
        None
        if "expected_length" in test_case
        else test_case["expected"]["bng_ref_formatted"]
    )
    expected_length = None if "expected" in test_case else test_case["expected_length"]

    if "expected_length" in test_case:
        # Assert that the function returns the expected length
        assert len(bng_kring(BNGReference(bng_ref_string), k)) == expected_length

    elif "expected_warning" in test_case:
        # Assert that the test case raises a warning
        with pytest.warns(UserWarning):
            # Assert that the function returns the expected result
            kring = bng_kring(BNGReference(bng_ref_string), k)
            assert sorted([r.bng_ref_formatted for r in kring]) == sorted(expected)

    else:
        # Assert that the function returns the expected result
        kring = bng_kring(BNGReference(bng_ref_string), k)
        assert sorted([r.bng_ref_formatted for r in kring]) == sorted(expected)


class BNGKDiscTestCase(TypedDict):
    """TypedDict for bng_kdisc function test cases.

    Attributes:
        bng_ref_string (str): The BNG reference string.
        k (int): The k value for the k-disc.
        expected_warning (bool | None): The expected warning is a boolean indicating if
            a warning is expected.
        expected (dict[str, list[str]] | None): The expected result is a dictionary with
            the key "bng_ref_formatted" and a list of formatted BNG reference strings.
        expected_length (int | None): The expected length of the k-disc. Represents the
            number of BNGReference objects within k-disc.
    """

    bng_ref_string: str
    k: int
    expected_warning: bool | None
    expected: dict[str, list[str]] | None
    expected_length: int | None


# Parameterised test for bng_kdisc function
@pytest.mark.parametrize(
    "test_case",
    # Load test cases from JSON file
    _load_test_cases(
        file_path=Path(__file__).parent / "data" / "traversal_test_cases.json"
    )["bng_kdisc"],
)
def test_bng_kdisc(test_case: BNGKDiscTestCase) -> None:
    """Test bng_kdisc with test cases from JSON file.

    Args:
        test_case (BNGKDiscTestCase): The test case from JSON file.
    """
    # Load test case data
    bng_ref_string = test_case["bng_ref_string"]
    k = test_case["k"]
    # Get expected result
    expected = (
        None
        if "expected_length" in test_case
        else test_case["expected"]["bng_ref_formatted"]
    )
    expected_length = None if "expected" in test_case else test_case["expected_length"]

    if "expected_length" in test_case:
        # Assert that the function returns the expected length
        assert len(bng_kdisc(BNGReference(bng_ref_string), k)) == expected_length

    elif "expected_warning" in test_case:
        # Assert that the test case raises a warning
        with pytest.warns(UserWarning):
            # Assert that the function returns the expected result
            kdisc = bng_kdisc(BNGReference(bng_ref_string), k)
            assert sorted([r.bng_ref_formatted for r in kdisc]) == sorted(expected)

    else:
        # Assert that the function returns the expected result
        kdisc = bng_kdisc(BNGReference(bng_ref_string), k)
        assert sorted([r.bng_ref_formatted for r in kdisc]) == sorted(expected)


class BNGKDWithinTestCase(TypedDict):
    """TypedDict for bng_dwithin function test cases.

    Attributes:
        bng_ref_string (str): The BNG reference string.
        d (int): The d value for the d-within search.
        expected (dict[str, list[str]] | None): The expected result is a dictionary with
            the key "bng_ref_formatted" and a list of formatted BNG reference strings.
        expected_length (int | None): The expected length of the d-within search.
            Represents the number of BNGReference objects within d-within search.
    """

    bng_ref_string: str
    d: int
    expected: dict[str, list[str]] | None
    expected_length: int | None


# Parameterised test for bng_dwithin function
@pytest.mark.parametrize(
    "test_case",
    # Load test cases from JSON file
    _load_test_cases(
        file_path=Path(__file__).parent / "data" / "traversal_test_cases.json"
    )["bng_dwithin"],
)
def test_bng_dwithin(test_case: BNGKDWithinTestCase) -> None:
    """Test bng_dwithin with test cases from JSON file.

    Args:
        test_case (BNGKDWithinTestCase): The test case from JSON file.
    """
    if "expected_length" in test_case:
        # Assert that the function returns the expected length
        assert (
            len(bng_dwithin(BNGReference(test_case["bng_ref_string"]), test_case["d"]))
            == test_case["expected_length"]
        )
    else:
        # Assert that the function returns the expected result
        kring = bng_dwithin(BNGReference(test_case["bng_ref_string"]), test_case["d"])
        assert sorted([r.bng_ref_formatted for r in kring]) == sorted(
            test_case["expected"]["bng_ref_formatted"]
        )
