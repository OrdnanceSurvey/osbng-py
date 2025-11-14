"""Testing for the indexing_gpd module.

Testing is skipped if the GeoPandas (https://github.com/geopandas/geopandas) package is
not installed.

The test cases are defined in the JSON file located at ./data/indexing_test_cases.json
and are used to parameterise the tests for various functions in the indexing module.
Test cases are loaded from the JSON file using the _load_test_cases function, which is
defined in the utils module. The test cases are defined as TypedDicts, which provide a
way to define the structure of the test case data.

Testing reuses the test cases for the osbng.indexing.geom_to_bng_intersection function.
"""

from math import sqrt
from pathlib import Path

import pytest

# Skip tests if geopandas package is not installed
# Match minimum geopandas version to (optional) dependency in pyproject.toml
pytest.importorskip(
    "geopandas",
    minversion="1.0.0",
    reason="The 'geopandas' package is required for 'indexing_gpd' tests.",
)

import geopandas as gpd
from shapely.geometry import shape

from osbng.errors import _EXCEPTION_MAP
from osbng.indexing import _validate_and_normalise_bng_resolution
from osbng.indexing_gpd import gdf_to_bng_intersection_explode
from osbng.utils import _load_test_cases
from tests.test_indexing import GeomToBNGIntersectionTestCase


def validate_and_assert_gdf_bng_intersection(
    gdf: gpd.GeoDataFrame, resolution: int | str, expected: list[tuple[str, bool]]
) -> None:
    """Validates and asserts gdf_to_bng_intersection_explode return.

    Args:
        gdf (gpd.GeoDataFrame): GeoPandas GeoDataFrame containing the geometry to be
            tested.
        resolution (int | str): The resolution expressed either as a metre-based
            integer or as a string label.
        expected (list[tuple[str, bool]]): Expected result. A list of tuples, where
            each tuple contains, the expected BNG reference formatted string and a
            boolean indicating if it is a core geometry.
    """
    # Apply the gdf_to_bng_intersection_explode function to the input GeoDataFrame
    gdf_test = gdf_to_bng_intersection_explode(gdf, resolution)
    # Assert that the result is a GeoDataFrame
    assert isinstance(gdf_test, gpd.GeoDataFrame)

    # Extract the 'bng_ref_formatted' property from the 'bng_ref' column
    # and 'is_core' column
    result = [
        (bng_ref.bng_ref_formatted, is_core)
        for bng_ref, is_core in zip(gdf_test["bng_ref"], gdf_test["is_core"])
    ]
    # Assert that the result matches the expected output
    assert sorted(result) == sorted(expected)

    # Extract the areas of the core indexed geometries
    # Core indexed geometries represent grid squares that are fully contained within
    # the input geometry
    result_core_areas = gdf_test[gdf_test["is_core"]]["geometry"].area.tolist()

    if result_core_areas:
        # Normalise the resolution to its metre equivalent
        normalised_resolution = _validate_and_normalise_bng_resolution(resolution)
        # Assert that the resolution of the core indexed geometries
        # is equal to the normalised resolution
        assert all(sqrt(area) == normalised_resolution for area in result_core_areas)


# Parameterised test for gdf_to_bng_intersection_explode function
@pytest.mark.parametrize(
    "test_case",
    # Load test cases from JSON file
    # Reuses test cases for the osbng.indexing.geom_to_bng_intersection function
    _load_test_cases(
        file_path=Path(__file__).parent / "data" / "indexing_test_cases.json"
    )["geom_to_bng_intersection"],
)
def test_gdf_to_bng_intersection_explode(
    test_case: GeomToBNGIntersectionTestCase,
) -> None:
    """Test gdf_to_bng_intersection_explode with test cases from JSON file.

    Args:
        test_case (GeomToBNGIntersectionTestCase): Test case from JSON file.
    """
    # Load test case data
    # Convert test case geometry from GeoJSON to Shapely Geometry object
    geom = shape(test_case["geom"])
    # Create GeoDataFrame from the geometry
    # Set GeoDataFrame coordinate reference system (CRS) to
    # 'EPSG:27700' (British National Grid)
    gdf = gpd.GeoDataFrame({"geometry": [geom]}, crs=27700)
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
            gdf_to_bng_intersection_explode(gdf, resolution)

    elif "expected_warning" in test_case:
        # Assert that the test case raises a warning
        with pytest.warns(UserWarning):
            # Assert that the function returns the expected result
            validate_and_assert_gdf_bng_intersection(gdf, resolution, expected)

    else:
        # Assert that the function returns the expected result
        validate_and_assert_gdf_bng_intersection(gdf, resolution, expected)
