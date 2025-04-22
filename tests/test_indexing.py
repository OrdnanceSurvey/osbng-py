"""Testing for the indexing module.

Test cases are loaded from a JSON file using the _load_test_cases function from the utils module.
"""

from math import sqrt

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


# Parameterised test for _validate_and_normalise_bng_resolution function
@pytest.mark.parametrize(
    "test_case",
    # Load test cases from JSON file
    _load_test_cases(file_path="./data/indexing_test_cases.json")[
        "_validate_and_normalise_bng_resolution"
    ],
)
def test__validate_and_normalise_bng_resolution(test_case):
    """Test _validate_and_normalise_bng_resolution with test cases from JSON file.

    Args:
        test_case (dict): Test case from JSON file.
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


# Parameterised test for _validate_easting_northing function
@pytest.mark.parametrize(
    "test_case",
    # Load test cases from JSON file
    _load_test_cases(file_path="./data/indexing_test_cases.json")[
        "_validate_easting_northing"
    ],
)
def test__validate_easting_northing(test_case):
    """Test _validate_and_normalise_bng_resolution with test cases from JSON file.

    Args:
        test_case (dict): Test case from JSON file.
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
        try:
            _validate_easting_northing(easting, northing)
        except Exception as e:
            pytest.fail(f"Unexpected exception raised: {e}")


# Parameterised test for _validate_and_normalise_bbox function
@pytest.mark.parametrize(
    "test_case",
    # Load test cases from JSON file
    _load_test_cases(file_path="./data/indexing_test_cases.json")[
        "_validate_and_normalise_bbox"
    ],
)
def test__validate_and_normalise_bbox(test_case):
    """Test _validate_and_normalise_bbox with test cases from JSON file.

    Args:
        test_case (dict): Test case from JSON file.
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


# Parameterised test for _get_bng_suffix function
@pytest.mark.parametrize(
    "test_case",
    # Load test cases from JSON file
    _load_test_cases(file_path="./data/indexing_test_cases.json")["_get_bng_suffix"],
)
def test__get_bng_suffix(test_case):
    """Test _get_bng_suffix function with test cases from JSON file.

    Args:
        test_case (dict): Test case from JSON file.
    """
    # Load test case data
    easting = test_case["easting"]
    northing = test_case["northing"]
    resolution = test_case["resolution"]
    expected = test_case["expected"]

    # Assert that the function returns the expected result
    assert _get_bng_suffix(easting, northing, resolution) == expected


# Parameterised test for _decompose_geom function
@pytest.mark.parametrize(
    "test_case",
    # Load test cases from JSON file
    _load_test_cases(file_path="./data/indexing_test_cases.json")["_decompose_geom"],
)
def test__decompose_geom(test_case):
    """Test _decompose_geom with test cases from JSON file.

    Args:
        test_case (dict): Test case from JSON file.
    """
    # Load test case data
    geom = test_case["geom"]
    expected_count = test_case["expected"]["count"]
    expected_types = test_case["expected"]["types"]

    # Convert test case geometry from GeoJSON to Shapely Geometry object
    # Decompose geometry into its constituent parts
    parts = _decompose_geom(shape(geom))

    # Assert that the decomposition returns the expected part count
    assert len(parts) == expected_count
    # Assert that the decomposition returns the expected part types
    types = [part.geom_type for part in parts]
    assert sorted(types) == sorted(expected_types)


# Parameterised test for xy_to_bng function
@pytest.mark.parametrize(
    "test_case",
    # Load test cases from JSON file
    _load_test_cases(file_path="./data/indexing_test_cases.json")["xy_to_bng"],
)
def test_xy_to_bng(test_case):
    """Test xy_to_bng with test cases from JSON file.

    Args:
        test_case (dict): Test case from JSON file.
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


# Parameterised test for bng_to_xy function
@pytest.mark.parametrize(
    "test_case",
    # Load test cases from JSON file
    _load_test_cases(file_path="./data/indexing_test_cases.json")["bng_to_xy"],
)
def test_bng_to_xy(test_case):
    """Test bng_to_xy with test cases from JSON file.

    Args:
        test_case (dict): Test case from JSON file.
    """
    # Load test case data
    bng_ref_string = test_case["bng_ref_string"]
    position = test_case["position"]
    # Get expected result as tuple
    expected = tuple(test_case["expected"])

    # Create BNGReference object
    bng_ref = BNGReference(bng_ref_string)

    # Assert that the function returns the expected result
    assert bng_to_xy(bng_ref, position) == expected


# Parameterised test for bng_to_bbox function
@pytest.mark.parametrize(
    "test_case",
    # Load test cases from JSON file
    _load_test_cases(file_path="./data/indexing_test_cases.json")["bng_to_bbox"],
)
def test_bng_to_bbox(test_case):
    """Test bng_to_bbox with test cases from JSON file.

    Args:
        test_case (dict): Test case from JSON file.
    """
    # Load test case data
    bng_ref_string = test_case["bng_ref_string"]
    # Get expected result as tuple
    expected = tuple(test_case["expected"])

    # Create BNGReference object
    bng_ref = BNGReference(bng_ref_string)

    # Assert that the function returns the expected result
    assert bng_to_bbox(bng_ref) == expected


# Parameterised test for bng_to_grid_geom function
@pytest.mark.parametrize(
    "test_case",
    # Load test cases from JSON file
    _load_test_cases(file_path="./data/indexing_test_cases.json")["bng_to_grid_geom"],
)
def test_bng_to_grid_geom(test_case):
    """Test bng_to_grid_geom with test cases from JSON file.

    Args:
        test_case (dict): Test case from JSON file.
    """
    # Load test case data
    bng_ref_string = test_case["bng_ref_string"]
    # Convert expected result from GeoJSON to Shapely geometry object
    expected = shape(test_case["expected"])

    # Create BNGReference object
    bng_ref = BNGReference(bng_ref_string)

    # Assert that the the two geometries are equal
    # Normalise geometries to account for coordinate order differences
    assert_geometries_equal(bng_to_grid_geom(bng_ref), expected, normalize=True)


# Parameterised test for bbox_to_bng function
@pytest.mark.parametrize(
    "test_case",
    # Load test cases from JSON file
    _load_test_cases(file_path="./data/indexing_test_cases.json")["bbox_to_bng"],
)
def test_bbox_to_bng(test_case):
    """Test bbox_to_bng with test cases from JSON file.

    Args:
        test_case (dict): Test case from JSON file.
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


# Parameterised test for geom_to_bng function
@pytest.mark.parametrize(
    "test_case",
    # Load test cases from JSON file
    _load_test_cases(file_path="./data/indexing_test_cases.json")["geom_to_bng"],
)
def test_geom_to_bng(test_case):
    """Test geom_to_bng with test cases from JSON file.

    Args:
        test_case (dict): Test case from JSON file.
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
            bng_refs = geom_to_bng(shape(geom), resolution)

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


# Parameterised test for geom_to_bng_intersection function
@pytest.mark.parametrize(
    "test_case",
    # Load test cases from JSON file
    _load_test_cases(file_path="./data/indexing_test_cases.json")[
        "geom_to_bng_intersection"
    ],
)
def test_geom_to_bng_intersection(test_case):
    """Test geom_to_bng_intersection with test cases from JSON file.

    Args:
        test_case (dict): Test case from JSON file.
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