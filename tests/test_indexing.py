"""Testing for the indexing module.


The test cases are defined in the JSON file located at ./data/indexing_test_cases.json and are used to parameterise the tests for various functions in the indexing module.
Test cases are loaded from the JSON file using the _load_test_cases function, which is defined in the utils module.
The test cases are defined as TypedDicts, which provide a way to define the structure of the test case data.
"""

from math import sqrt
from typing import Any, TypedDict

import pytest

from shapely import Geometry
from shapely.geometry import shape
from shapely.testing import assert_geometries_equal

from osbng.bng_reference import BNGReference
from osbng.errors import _EXCEPTION_MAP
from osbng.indexing import (
    _validate_and_normalise_bng_resolution,
    _validate_easting_northing,
    _validate_and_normalise_bbox,
    _get_bng_suffix,
    _decompose_geom,
    xy_to_bng,
    bng_to_xy,
    bng_to_bbox,
    bng_to_grid_geom,
    bbox_to_bng,
    geom_to_bng,
    geom_to_bng_intersection,
)
from osbng.utils import _load_test_cases


class ValidateAndNormaliseBNGResolutionTestCase(TypedDict):
    """TypedDict for _validate_and_normalise_bng_resolution function test cases.

    Attributes:
        resolution (int | float | str): The BNG resolution expressed either as a metre-based integer or float, or as a string label.
        expected (int | None): The expected result is an integer or None if exception is expected.
        expected_exception (dict[str, str] | None): The expected exception is a dictionary with the exception name.
    """

    resolution: int | float | str
    expected: int | None
    expected_exception: dict[str, str] | None


# Parameterised test for _validate_and_normalise_bng_resolution function
@pytest.mark.parametrize(
    "test_case",
    # Load test cases from JSON file
    _load_test_cases(file_path="./data/indexing_test_cases.json")[
        "_validate_and_normalise_bng_resolution"
    ],
)
def test__validate_and_normalise_bng_resolution(
    test_case: ValidateAndNormaliseBNGResolutionTestCase,
):
    """Test _validate_and_normalise_bng_resolution with test cases from JSON file.

    Args:
        test_case (ValidateAndNormaliseBNGResolutionTestCase): Test case from JSON file.
    """
    # Load test case data
    resolution = test_case["resolution"]

    if "expected_exception" in test_case:
        # Get exception name from test case
        exception_name = test_case["expected_exception"]["name"]
        # Get exception class from name
        exception_class = _EXCEPTION_MAP[exception_name]
        # Assert that the test case raises the expected exception
        with pytest.raises(exception_class):
            _validate_and_normalise_bng_resolution(resolution)

    else:
        # Get expected result
        expected = test_case["expected"]
        # Assert that the function returns the expected result
        assert _validate_and_normalise_bng_resolution(resolution) == expected


class ValidateEastingNorthingTestCase(TypedDict):
    """TypedDict for _validate_easting_northing function test cases.

    Attributes:
        easting (int | float): The easting coordinate.
        northing (int | float): The northing coordinate.
        expected_exception (dict[str, str] | None): The expected exception is a dictionary with the exception name.
    """

    easting: int | float
    northing: int | float
    expected_exception: dict[str, str] | None


# Parameterised test for _validate_easting_northing function
@pytest.mark.parametrize(
    "test_case",
    # Load test cases from JSON file
    _load_test_cases(file_path="./data/indexing_test_cases.json")[
        "_validate_easting_northing"
    ],
)
def test__validate_easting_northing(test_case: ValidateEastingNorthingTestCase):
    """Test _validate_and_normalise_bng_resolution with test cases from JSON file.

    Args:
        test_case (ValidateEastingNorthingTestCase): Test case from JSON file.
    """
    # Load test case data
    easting = test_case["easting"]
    northing = test_case["northing"]

    if "expected_exception" in test_case:
        # Get exception name from test case
        exception_name = test_case["expected_exception"]["name"]
        # Get exception class from name
        exception_class = _EXCEPTION_MAP[exception_name]
        # Assert that the test case raises the expected exception
        with pytest.raises(exception_class):
            _validate_easting_northing(easting, northing)

    else:
        # Assert that the function returns the expected result
        _validate_easting_northing(easting, northing)


class ValidateAndNormaliseBBOXTestCase(TypedDict):
    """TypedDict for _validate_and_normalise_bbox function test cases.

    Attributes:
        xmin (int | float): The minimum easting coordinate of the bounding box.
        ymin (int | float): The minimum northing coordinate of the bounding box.
        xmax (int | float): The maximum easting coordinate of the bounding box.
        ymax (int | float): The maximum northing coordinate of the bounding box.
        expected_warning (bool | None): The expected warning is a boolean indicating if a warning is expected.
        expected (list[int | float]): The expected result is a list of bounding box coordinates.
    """

    xmin: int | float
    ymin: int | float
    xmax: int | float
    ymax: int | float
    expected_warning: bool | None
    expected: list[int | float]


# Parameterised test for _validate_and_normalise_bbox function
@pytest.mark.parametrize(
    "test_case",
    # Load test cases from JSON file
    _load_test_cases(file_path="./data/indexing_test_cases.json")[
        "_validate_and_normalise_bbox"
    ],
)
def test__validate_and_normalise_bbox(test_case: ValidateAndNormaliseBBOXTestCase):
    """Test _validate_and_normalise_bbox with test cases from JSON file.

    Args:
        test_case (ValidateAndNormaliseBBOXTestCase): Test case from JSON file.
    """
    # Load test case data
    xmin = test_case["xmin"]
    ymin = test_case["ymin"]
    xmax = test_case["xmax"]
    ymax = test_case["ymax"]
    # Get expected result as tuple
    expected = tuple(test_case["expected"])

    if "expected_warning" in test_case:
        # Assert that the test case raises a warning
        with pytest.warns(UserWarning):
            # Assert that the function returns the expected result
            assert _validate_and_normalise_bbox(xmin, ymin, xmax, ymax) == expected

    else:
        # Assert that the function returns the expected result
        assert _validate_and_normalise_bbox(xmin, ymin, xmax, ymax) == expected


class GetBNGSuffixTestCase(TypedDict):
    """TypedDict for _get_bng_suffix function test cases.

    Attributes:
        easting (int | float): The easting coordinate.
        northing (int | float): The northing coordinate.
        resolution (int): The resolution expressed as a metre-based integer.
        expected (str): The expected result is a BNG reference formatted string.
    """

    easting: int | float
    northing: int | float
    resolution: int
    expected: str


# Parameterised test for _get_bng_suffix function
@pytest.mark.parametrize(
    "test_case",
    # Load test cases from JSON file
    _load_test_cases(file_path="./data/indexing_test_cases.json")["_get_bng_suffix"],
)
def test__get_bng_suffix(test_case: GetBNGSuffixTestCase):
    """Test _get_bng_suffix function with test cases from JSON file.

    Args:
        test_case (GetBNGSuffixTestCase): Test case from JSON file.
    """
    # Load test case data
    easting = test_case["easting"]
    northing = test_case["northing"]
    resolution = test_case["resolution"]
    expected = test_case["expected"]

    # Assert that the function returns the expected result
    assert _get_bng_suffix(easting, northing, resolution) == expected


class DecomposeGeomTestCase(TypedDict):
    """TypedDict for _decompose_geom function test cases.

    Attributes:
        geom (dict[str, Any]): Geometry reresented in GeoJSON format.
        expected (dict[str, int | list[str]]): Expected result is a dictionary with the expected part count and list of part geometry types.
    """

    geom: dict[str, Any]
    expected: dict[str, int | list[str]]


# Parameterised test for _decompose_geom function
@pytest.mark.parametrize(
    "test_case",
    # Load test cases from JSON file
    _load_test_cases(file_path="./data/indexing_test_cases.json")["_decompose_geom"],
)
def test__decompose_geom(test_case: DecomposeGeomTestCase):
    """Test _decompose_geom with test cases from JSON file.

    Args:
        test_case (DecomposeGeomTestCase): Test case from JSON file.
    """
    # Load test case data
    # Convert test case geometry from GeoJSON to Shapely Geometry object
    geom = shape(test_case["geom"])
    expected_count = test_case["expected"]["count"]
    expected_types = test_case["expected"]["types"]

    # Decompose geometry into its constituent parts
    parts = _decompose_geom(geom)

    # Assert that the decomposition returns the expected part count
    assert len(parts) == expected_count
    # Assert that the decomposition returns the expected part types
    types = [part.geom_type for part in parts]
    assert sorted(types) == sorted(expected_types)


class XYToBNGTestCase(TypedDict):
    """TypedDict for xy_to_bng function test cases.

    Attributes:
        easting (int | float): The easting coordinate.
        northing (int | float): The northing coordinate.
        resolution (int | str): The resolution expressed either as a metre-based integer or as a string label.
        expected (dict[str, str] | None): The expected result is a dictionary with the BNG reference formatted string.
        expected_exception (dict[str, str] | None): The expected exception is a dictionary with the exception name.
    """

    easting: int | float
    northing: int | float
    resolution: int | str
    expected: dict[str, str] | None
    expected_exception: dict[str, str] | None


# Parameterised test for xy_to_bng function
@pytest.mark.parametrize(
    "test_case",
    # Load test cases from JSON file
    _load_test_cases(file_path="./data/indexing_test_cases.json")["xy_to_bng"],
)
def test_xy_to_bng(test_case: XYToBNGTestCase):
    """Test xy_to_bng with test cases from JSON file.

    Args:
        test_case (XYToBNGTestCase): Test case from JSON file.
    """
    # Load test case data
    easting = test_case["easting"]
    northing = test_case["northing"]
    resolution = test_case["resolution"]

    if "expected_exception" in test_case:
        # Get exception name from test case
        exception_name = test_case["expected_exception"]["name"]
        # Get exception class from name
        exception_class = _EXCEPTION_MAP[exception_name]
        # Assert that the test case raises the expected exception
        with pytest.raises(exception_class):
            xy_to_bng(easting, northing, resolution)

    else:
        # Get expected result
        expected = test_case["expected"]["bng_ref_formatted"]
        # Create BNGReference object
        bng_ref = xy_to_bng(easting, northing, resolution)
        # Assert that the function returns the expected result
        assert bng_ref.bng_ref_formatted == expected


class BNGToXYTestCase(TypedDict):
    """TypedDict for bng_to_xy function test cases.

    Attributes:
        bng_ref_formatted (str): The BNG reference formatted string.
        position (str): The grid cell position expressed as a string.
        expected (list[float | int]): The expected result is a list of easting and northing coordinates.
    """

    bng_ref_formatted: str
    position: int | str
    expected: list[int | float]


# Parameterised test for bng_to_xy function
@pytest.mark.parametrize(
    "test_case",
    # Load test cases from JSON file
    _load_test_cases(file_path="./data/indexing_test_cases.json")["bng_to_xy"],
)
def test_bng_to_xy(test_case: BNGToXYTestCase):
    """Test bng_to_xy with test cases from JSON file.

    Args:
        test_case (BNGToXYTestCase): Test case from JSON file.
    """
    # Load test case data
    bng_ref_string = test_case["bng_ref_formatted"]
    position = test_case["position"]
    # Get expected result as tuple
    expected = tuple(test_case["expected"])

    # Create BNGReference object
    bng_ref = BNGReference(bng_ref_string)

    # Assert that the function returns the expected result
    assert bng_to_xy(bng_ref, position) == expected


class BNGToBBOXTestCase(TypedDict):
    """TypedDict for bng_to_bbox function test cases.

    Attributes:
        bng_ref_formatted (str): The BNG reference formatted string.
        expected (list[int]): The expected result is a list of bounding box coordinates.
    """

    bng_ref_formatted: str
    expected: list[int]


# Parameterised test for bng_to_bbox function
@pytest.mark.parametrize(
    "test_case",
    # Load test cases from JSON file
    _load_test_cases(file_path="./data/indexing_test_cases.json")["bng_to_bbox"],
)
def test_bng_to_bbox(test_case: BNGToBBOXTestCase):
    """Test bng_to_bbox with test cases from JSON file.

    Args:
        test_case (BNGToBBOXTestCase): Test case from JSON file.
    """
    # Load test case data
    bng_ref_string = test_case["bng_ref_formatted"]
    # Get expected result as tuple
    expected = tuple(test_case["expected"])

    # Create BNGReference object
    bng_ref = BNGReference(bng_ref_string)

    # Assert that the function returns the expected result
    assert bng_to_bbox(bng_ref) == expected


class BNGToGridGeomTestCase(TypedDict):
    """TypedDict for bng_to_grid_geom function test cases.

    Attributes:
        bng_ref_formatted (str): The BNG reference formatted string.
        expected (dict[str, Any]): The expected result is a dictionary with the expected geometry in GeoJSON format.
    """

    bng_ref_formatted: str
    expected: dict[str, Any]


# Parameterised test for bng_to_grid_geom function
@pytest.mark.parametrize(
    "test_case",
    # Load test cases from JSON file
    _load_test_cases(file_path="./data/indexing_test_cases.json")["bng_to_grid_geom"],
)
def test_bng_to_grid_geom(test_case: BNGToGridGeomTestCase):
    """Test bng_to_grid_geom with test cases from JSON file.

    Args:
        test_case (BNGToGridGeomTestCase): Test case from JSON file.
    """
    # Load test case data
    bng_ref_string = test_case["bng_ref_formatted"]
    # Convert expected result from GeoJSON to Shapely geometry object
    expected = shape(test_case["expected"])

    # Create BNGReference object
    bng_ref = BNGReference(bng_ref_string)

    # Assert that the the two geometries are equal
    # Normalise geometries to account for coordinate order differences
    assert_geometries_equal(bng_to_grid_geom(bng_ref), expected, normalize=True)


class BBOXToBNGTestCase(TypedDict):
    """TypedDict for bbox_to_bng function test cases.

    Attributes:
        xmin (int | float): The minimum easting coordinate of the bounding box.
        ymin (int | float): The minimum northing coordinate of the bounding box.
        xmax (int | float): The maximum easting coordinate of the bounding box.
        ymax (int | float): The maximum northing coordinate of the bounding box.
        resolution (int | str): The resolution expressed either as a metre-based integer or as a string label.
        expected_warning (bool | None): The expected warning is a boolean indicating if a warning is expected.
        expected (dict[str, list[str]]): The expected result is a dictionary with a list of BNG reference formatted strings.
    """

    xmin: int | float
    ymin: int | float
    xmax: int | float
    ymax: int | float
    resolution: int | str
    expected_warning: bool | None
    expected: dict[str, list[str]]


# Parameterised test for bbox_to_bng function
@pytest.mark.parametrize(
    "test_case",
    # Load test cases from JSON file
    _load_test_cases(file_path="./data/indexing_test_cases.json")["bbox_to_bng"],
)
def test_bbox_to_bng(test_case: BBOXToBNGTestCase):
    """Test bbox_to_bng with test cases from JSON file.

    Args:
        test_case (BBOXToBNGTestCase): Test case from JSON file.
    """
    # Load test case data
    xmin = test_case["xmin"]
    ymin = test_case["ymin"]
    xmax = test_case["xmax"]
    ymax = test_case["ymax"]
    resolution = test_case["resolution"]
    # Get expected result
    expected = test_case["expected"]["bng_ref_formatted"]

    if "expected_warning" in test_case:
        # Assert that the function raises a warning
        with pytest.warns(UserWarning):
            # Return a list of BNGReference objects
            bng_refs = bbox_to_bng(xmin, ymin, xmax, ymax, resolution)
            # Sort lists to account for order differences
            bng_ref_strings = [bng_ref.bng_ref_formatted for bng_ref in bng_refs]
            # Assert that the function returns the expected result
            assert sorted(bng_ref_strings) == sorted(expected)

    else:
        # Return a list of BNGReference objects
        bng_refs = bbox_to_bng(xmin, ymin, xmax, ymax, resolution)
        # Assert that the function returns the expected result
        # Sort lists to account for order differences
        bng_ref_strings = [bng_ref.bng_ref_formatted for bng_ref in bng_refs]
        # Assert that the function returns the expected result
        assert sorted(bng_ref_strings) == sorted(expected)


class GeomToBNGTestCase(TypedDict):
    """TypedDict for geom_to_bng function test cases.

    Attributes:
        geom (dict[str, Any]): Geometry represented in GeoJSON format.
        resolution (int | str): The resolution expressed either as a metre-based integer or as a string label.
        expected_exception (dict[str, str] | None): The expected exception is a dictionary with the exception name.
        expected_warning (bool | None): The expected warning is a boolean indicating if a warning is expected.
        expected (dict[str, list[str]] | None): The expected result is a dictionary with a list of BNG reference formatted strings.
    """

    geom: dict[str, Any]
    resolution: int | str
    expected_exception: dict[str, str] | None
    expected_warning: bool | None
    expected: dict[str, list[str]] | None


# Parameterised test for geom_to_bng function
@pytest.mark.parametrize(
    "test_case",
    # Load test cases from JSON file
    _load_test_cases(file_path="./data/indexing_test_cases.json")["geom_to_bng"],
)
def test_geom_to_bng(test_case: GeomToBNGTestCase):
    """Test geom_to_bng with test cases from JSON file.

    Args:
        test_case (GeomToBNGTestCase): Test case from JSON file.
    """
    # Load test case data
    geom = test_case["geom"]
    resolution = test_case["resolution"]
    # Get expected result
    expected = (
        None
        if "expected_exception" in test_case
        else test_case["expected"]["bng_ref_formatted"]
    )

    if "expected_exception" in test_case:
        # Get exception name from test case
        exception_name = test_case["expected_exception"]["name"]
        # Get exception class from name
        exception_class = _EXCEPTION_MAP[exception_name]
        # Assert that the test case raises the expected exception
        with pytest.raises(exception_class):
            geom_to_bng(shape(geom), resolution)

    elif "expected_warning" in test_case:
        # Assert that the function raises a warning
        with pytest.warns(UserWarning):
            # Convert test case geometry from GeoJSON to Shapely Geometry object
            # Return a list of BNGReference objects
            bng_refs = geom_to_bng(shape(geom), resolution)
            # Sort lists to account for order differences
            bng_ref_strings = [bng_ref.bng_ref_formatted for bng_ref in bng_refs]
            # Assert that the function returns the expected result
            assert sorted(bng_ref_strings) == sorted(expected)

    else:
        # Convert test case geometry from GeoJSON to Shapely Geometry object
        # Return a list of BNGReference objects
        bng_refs = geom_to_bng(shape(geom), resolution)
        # Sort lists to account for order differences
        bng_ref_strings = [bng_ref.bng_ref_formatted for bng_ref in bng_refs]
        # Assert that the function returns the expected result
        assert sorted(bng_ref_strings) == sorted(expected)


def validate_and_assert_bng_intersection(
    geom: Geometry, resolution: int | str, expected: dict[str, str | bool]
):
    """Helper function to validate and assert BNGIndexedGeometry results.

    Args:
        geom (Geometry): Shapely Geometry object.
        resolution (int | str): The resolution of the BNG reference expressed either as a metre-based integer or as a string label.
        expected (dict[str, str | bool]): Expected result. A dictionary containing the expected BNG reference formatted string and a boolean indicating if it is a core geometry.
    """
    # Convert test case geometry from GeoJSON to Shapely Geometry object
    # Return a list of BNGIndexedGeometry objects
    bng_idx_geoms = geom_to_bng_intersection(shape(geom), resolution)
    # Extract bng_ref_formatted and is_core properties to create a simplified representation
    # of the BNGIndexedGeometry objects for comparison with the expected output.
    result = [
        (bng_idx_geom.bng_ref.bng_ref_formatted, bng_idx_geom.is_core)
        for bng_idx_geom in bng_idx_geoms
    ]
    # Assert that the result matches the expected output
    assert sorted(result) == sorted(expected)
    # Extract the areas of the core indexed geometries
    # Core indexed geometries represent grid squares that are fully contained within the input geometry
    result_core_areas = [
        bng_idx_geom.geom.area for bng_idx_geom in bng_idx_geoms if bng_idx_geom.is_core
    ]
    if result_core_areas:
        # Normalise the resolution to its metre equivalent
        normalised_resolution = _validate_and_normalise_bng_resolution(resolution)
        # Assert that the resolution of the core indexed geometries is equal to the normalised resolution
        assert all(sqrt(area) == normalised_resolution for area in result_core_areas)


class GeomToBNGIntersectionTestCase(TypedDict):
    """TypedDict for geom_to_bng_intersection function test cases.

    Attributes:
        geom (dict[str, Any]): Geometry represented in GeoJSON format.
        resolution (int | str): The resolution expressed either as a metre-based integer or as a string label.
        expected_exception (dict[str, str] | None): The expected exception is a dictionary with the exception name.
        expected_warning (bool | None): The expected warning is a boolean indicating if a warning is expected.
        expected (list[dict[str, str | bool]] | None): The expected result is a list of dictionaries with the expected BNG reference formatted strings and booleans indicating if a grid square is a core geometry.
    """

    geom: dict[str, Any]
    resolution: int | str
    expected_exception: dict[str, str] | None
    expected_warning: bool | None
    expected: list[dict[str, str | bool]] | None


# Parameterised test for geom_to_bng_intersection function
@pytest.mark.parametrize(
    "test_case",
    # Load test cases from JSON file
    _load_test_cases(file_path="./data/indexing_test_cases.json")[
        "geom_to_bng_intersection"
    ],
)
def test_geom_to_bng_intersection(test_case: GeomToBNGIntersectionTestCase):
    """Test geom_to_bng_intersection with test cases from JSON file.

    Args:
        test_case (GeomToBNGIntersectionTestCase): Test case from JSON file.
    """
    # Load test case data
    # Convert test case geometry from GeoJSON to Shapely Geometry object
    geom = shape(test_case["geom"])
    resolution = test_case["resolution"]
    # Convert expected result dictionary values into tuples
    expected = (
        None
        if "expected_exception" in test_case
        else [
            (item["bng_ref_formatted"], item["is_core"])
            for item in test_case["expected"]
        ]
    )

    if "expected_exception" in test_case:
        # Get exception name from test case
        exception_name = test_case["expected_exception"]["name"]
        # Get exception class from name
        exception_class = _EXCEPTION_MAP[exception_name]
        # Assert that the test case raises an exception
        with pytest.raises(exception_class):
            geom_to_bng_intersection(shape(geom), resolution)

    elif "expected_warning" in test_case:
        # Assert that the test case raises a warning
        with pytest.warns(UserWarning):
            # Assert that the function returns the expected result
            validate_and_assert_bng_intersection(geom, resolution, expected)

    else:
        # Assert that the function returns the expected result
        validate_and_assert_bng_intersection(geom, resolution, expected)
