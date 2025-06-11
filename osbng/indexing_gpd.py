"""Provides functionality to convert geometries in a GeoPandas `GeoDataFrame` to `BNGIndexedGeometry` objects,
and explode the resulting lists into a flattened GeoDataFrame.

This module requires the 'GeoPandas' (https://github.com/geopandas/geopandas) package to be installed.

To install the required package, use::

    pip install osbng[geopandas]

"""

try:
    import geopandas as gpd
except ImportError as e:
    raise ImportError(
        "The 'geopandas' package is required to use the 'osbng.indexing_gdf' module. "
        "Install it with: pip install osbng[geopandas]"
    ) from e

from osbng.indexing import (
    _validate_and_normalise_bng_resolution,
    geom_to_bng_intersection,
)

__all__ = ["gdf_to_bng_intersection_explode"]


def gdf_to_bng_intersection_explode(
    gdf: gpd.GeoDataFrame,
    resolution: int | str,
    *,
    reset_index: bool = True,
) -> gpd.GeoDataFrame:
    """Applies the `osbng.indexing.geom_to_bng_intersection` function to each geometry in a GeoPandas `GeoDataFrame`, returning a flattened GeoDataFrame
    by exploding the resulting lists of `BNGIndexedGeometry` objects.

    This function decomposes each geometry in the input GeoDataFrame bounded by their presence in BNG grid squares at the specified resolution. The resulting `BNGIndexedGeometry` objects are
    exploded into individual rows, with each row containing a new column for each `BNGIndexedGeometry` object property: bng_ref, is_core, and geom.

    The original GeoDataFrame geometry column is replaced with the `geom` property of the `BNGIndexedGeometry` objects. The original geometry column can be retrieved if required
    by joining the resulting GeoDataFrame with the original GeoDataFrame on the index (if not reset), or using a feature identifier. Dropping the original geometry column reduces memory usage 
    and simplifies the resulting GeoDataFrame.

    Exploding the resulting GeoDataFrame allows for easier analysis and manipulation of the `BNGIndexedGeometry` object properties. This is otherwise a more complex operation.

    Args:
        gdf (gpd.GeoDataFrame): Input GeoDataFrame.
        resolution (int | str): The BNG resolution expressed either as a metre-based integer or as a string label.
        reset_index (bool): Whether to reset the index of the resulting GeoDataFrame. Defaults to True. Keyword-only.

    Returns:
        gpd.GeoDataFrame: A new GeoDataFrame with one row per `BNGIndexedGeometry` object, containing the following columns:
            - `bng_ref`: The `BNGReference` object. The `BNGIndexedGeometry` object `bng_ref` property.
            - `is_core`: A boolean indicating whether the geometry is a core grid square. The `BNGIndexedGeometry` object `is_core` property.
            - `geometry`: The Shapely Geometry representing the intersection between the input geometry and the grid square. The `BNGIndexedGeometry` object `geom` property.

    Raises:
        BNGResolutionError: If an invalid resolution is provided.
        BNGExtentError: If the coordinates of a Point geometry are outside of the BNG index system extent.
        TypeError: If the input is not a GeoPandas GeoDataFrame.
        ValueError: If the input GeoDataFrame is empty.
        ValueError: If the GeoDataFrame CRS is not equal to "EPSG:27700"
        ValueError: If an active geometry column is not set in the GeoDataFrame.
        ValueError: If the geometry type is not supported.
    """
    # Validate and normalise the resolution to its metre-based integer value
    validated_resolution = _validate_and_normalise_bng_resolution(resolution)

    # Validate the input is a GeoDataFrame
    if not isinstance(gdf, gpd.GeoDataFrame):
        raise TypeError("Input must be a GeoPandas GeoDataFrame.")
    
    # Validate the GeoDataFrame is not empty
    if gdf.empty:
        raise ValueError("Input GeoDataFrame must not be empty.")

    # Validate the GeoDataFrame coordinate reference system (CRS) is equal to EPSG:27700
    if gdf.crs is None or not gdf.crs.to_epsg() == 27700:
        raise ValueError(
            "GeoDataFrame CRS must be set to 'EPSG:27700' (British National Grid)."
        )

    # Validate if an active geometry column has been set on the GeoDataFrame
    geometry_column = gdf.active_geometry_name

    if geometry_column is None:
        raise ValueError(
            "GeoDataFrame must have an active geometry column set. "
            "Use `gdf.set_geometry(geometry_column_name)` to set the active geometry column."
        )

    # Initialise an empty list to store the rows for the new GeoDataFrame
    rows = []

    # Iterate over each row in the GeoDataFrame
    for idx, row in gdf.iterrows():
        # Extract the geometry from the specified geometry column
        geom = row[geometry_column]
        # Convert the geometry to BNGIndexedGeometry objects
        bng_idx_geoms = geom_to_bng_intersection(geom, validated_resolution)
        # Drop the geometry column from the original row
        orig_row = row.drop(geometry_column)

        # Iterate over BNGIndexedGeometry objects and create a new row for each
        for bng_idx_geom in bng_idx_geoms:
            # Copy original row columns to a new dictionary
            out_row = orig_row.to_dict()
            # Update the new row with BNGIndexedGeometry properties
            # Retain the original GeoDataFrame index for reference
            out_row.update(
                {
                    "bng_ref": bng_idx_geom.bng_ref,
                    "is_core": bng_idx_geom.is_core,
                    "geometry": bng_idx_geom.geom,
                    "orig_index": idx,
                }
            )
            # Append the new row to the list of rows
            rows.append(out_row)

    # Create a new GeoDataFrame from the list of rows
    out_gdf = gpd.GeoDataFrame(rows, geometry="geometry", crs=27700)

    if reset_index:
        # Drop the orig_index column if reset_index is True
        out_gdf = out_gdf.drop(columns=["orig_index"])
    else:
        # If reset_index is False, set the orig_index column as the index of the result GeoDataFrame
        out_gdf = out_gdf.set_index("orig_index")
        # Set GeoDataFrame to have an unamed index
        out_gdf.index.name = None

    return out_gdf
