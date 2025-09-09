"""Index geometries in a ``GeoPandas`` ``GeoDataFrame`` against the BNG index system.

Note:
    This module requires the `GeoPandas <https://github.com/geopandas/geopandas>`__
    package to be installed.

    To install the required package, use:

        pip install osbng[geopandas]

"""

from shapely import Geometry

try:
    import geopandas as gpd
except ImportError as e:
    raise ImportError(
        "The geopandas package is required to use the osbng.indexing_gdf module."
        "Install it with: pip install osbng[geopandas]"
    ) from e

from osbng.indexing import (
    _validate_and_normalise_bng_resolution,
    geom_to_bng_intersection,
)

__all__ = ["gdf_to_bng_intersection_explode"]


def _is_geometry_column(gdf: gpd.GeoDataFrame, col: str) -> bool:
    """Checks if a column in a ``GeoDataFrame`` is a geometry column.

    Args:
        gdf (gpd.GeoDataFrame): The ``GeoDataFrame`` to check.
        col (str): The column name to check.

    Returns:
        bool: True if the column is a geometry column, False otherwise.
    """
    # Drop NULL rows
    non_null = gdf[col].dropna()

    # If the column is empty, return False
    if non_null.empty:
        return False
    # Check if the first non-null value is an instance of Geometry
    return isinstance(non_null.iloc[0], Geometry)


def gdf_to_bng_intersection_explode(
    gdf: gpd.GeoDataFrame,
    resolution: int | str,
    *,
    reset_index: bool = True,
) -> gpd.GeoDataFrame:
    """Applies ``geom_to_bng_intersection`` to a ``GeoDataFrame`` at a given resolution.

    Decomposes each geometry in the input ``GeoDataFrame`` bounded by their presence in
    grid squares at the specified resolution. The resulting
    :class:`~osbng.indexing.BNGIndexedGeometry` objects are exploded into individual
    rows, with each row containing a new column for each
    :class:`~osbng.indexing.BNGIndexedGeometry` object property: ``bng_ref``,
    ``is_core``, and ``geom``.

    Notes:
        Decomposition is achieved by applying the
        :class:`~osbng.indexing.geom_to_bng_intersection` function to each geometry in
        the input ``GeoPandas`` ``GeoDataFrame``, returning a flattened ``GeoDataFrame``
        by exploding the resulting :class:`~osbng.indexing.BNGIndexedGeometry` lists.

        The input ``GeoDataFrame`` geometry column is replaced with the geom property of
        the :class:`~osbng.indexing.BNGIndexedGeometry` objects. The input geometry
        column can be retrieved if required by joining the resulting ``GeoDataFrame``
        with the original ``GeoDataFrame`` on the index (if not reset), or using a
        feature identifier. Dropping the original geometry column reduces memory usage
        and simplifies the resulting ``GeoDataFrame``.

        All non-geometry columns from the original ``GeoDataFrame`` are retained in the
        resulting ``GeoDataFrame``.

        Exploding the resulting ``GeoDataFrame`` allows for easier analysis and
        manipulation of the :class:`~osbng.indexing.BNGIndexedGeometry` object
        properties. This is otherwise a more complex operation.

    Warnings:
        The active geometry column of the input ``GeoDataFrame`` is passed to
        :class:`~osbng.indexing.geom_to_bng_intersection`, which is expected to be set
        and in the OSGB36 / British National Grid coordinate reference system (CRS)
        (EPSG:27700).

    Args:
        gdf (gpd.GeoDataFrame): Input ``GeoPandas`` ``GeoDataFrame``.
        resolution (int | str): The BNG resolution expressed either as a metre-based
            integer or as a string label.

    Keyword Args:
        reset_index (bool): Whether to reset the index of the resulting
          ``GeoDataFrame``, defaults to True.

    Returns:
        gpd.GeoDataFrame: A new ``GeoDataFrame`` with one row per
        :class:`~osbng.indexing.BNGIndexedGeometry` object, containing three columns
        bng_ref, is_core, and geometry corresponding to the
        :class:`~osbng.indexing.BNGIndexedGeometry` object properties.

    Raises:
        BNGResolutionError: If an invalid resolution is provided.
        BNGExtentError: If the coordinates of a Point geometry are outside of the BNG
            index system extent.
        TypeError: If the input is not a ``GeoPandas`` ``GeoDataFrame``.
        ValueError: If the ``GeoDataFrame`` CRS is not equal to "EPSG:27700"
        ValueError: If an active geometry column is not set in the ``GeoDataFrame``.
        ValueError: If the geometry type is not supported.

    Examples:
        >>> import geopandas as gpd
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...             "id": ["0", "1", "2"],
        ...             "geometry": [
        ...                 "POLYGON((530000 180000, 535000 180000, 535000 185000,
                             530000 185000, 530000 180000))",
        ...                 "POLYGON((540000 190000, 545000 190000, 545000 195000,
                            540000 195000, 540000 190000))",
        ...                 "POLYGON((550000 200000, 555000 200000, 555000 205000,
                            550000 205000, 550000 200000))"
        ...             ]
        ... })
        >>> gdf = gpd.GeoDataFrame(df, geometry=gpd.GeoSeries.from_wkt(df["geometry"]),
                                   crs="EPSG:27700")
        >>> gdf_to_bng_intersection_explode(gdf, resolution="1km")
            id                                            bng_ref
        0   0  BNGReference(bng_ref_formatted=TQ 31 80, resol...
        1   0  BNGReference(bng_ref_formatted=TQ 30 82, resol...
        2   0  BNGReference(bng_ref_formatted=TQ 33 84, resol...
        3   0  BNGReference(bng_ref_formatted=TQ 34 80, resol...
        4   0  BNGReference(bng_ref_formatted=TQ 33 80, resol...
        ..  ...                                                ...
        70  2  BNGReference(bng_ref_formatted=TL 52 01, resol...
        71  2  BNGReference(bng_ref_formatted=TL 52 03, resol...
        72  2  BNGReference(bng_ref_formatted=TL 50 04, resol...
        73  2  BNGReference(bng_ref_formatted=TL 50 03, resol...
        74  2  BNGReference(bng_ref_formatted=TL 54 01, resol...
            is_core                                       geometry
        0   True  POLYGON ((532000 180000, 532000 181000, 531000...
        1   True  POLYGON ((531000 182000, 531000 183000, 530000...
        2   True  POLYGON ((534000 184000, 534000 185000, 533000...
        3   True  POLYGON ((535000 180000, 535000 181000, 534000...
        4   True  POLYGON ((534000 180000, 534000 181000, 533000...
        ..   ...                                                ...
        70  True  POLYGON ((553000 201000, 553000 202000, 552000...
        71  True  POLYGON ((553000 203000, 553000 204000, 552000...
        72  True  POLYGON ((551000 204000, 551000 205000, 550000...
        73  True  POLYGON ((551000 203000, 551000 204000, 550000...
        74  True  POLYGON ((555000 201000, 555000 202000, 554000...
        [75 rows x 4 columns]

    See Also:
        :class:`~osbng.indexing.geom_to_bng_intersection` to index ``Shapely``
        geometries directly.

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
            "Use gdf.set_geometry(geometry_column_name) to set the active geometry "
            "column."
        )

    # Retain only the active geometry column and non-geometry columns
    gdf = gdf[
        [geometry_column]
        + [col for col in gdf.columns if not _is_geometry_column(gdf, col)]
    ]

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
        # If reset_index is False, set the orig_index column
        # as the index of the result GeoDataFrame
        out_gdf = out_gdf.set_index("orig_index")
        # Set GeoDataFrame to have an unamed index
        out_gdf.index.name = None

    return out_gdf
