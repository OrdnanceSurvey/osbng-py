"""Generate British National Grid (BNG) grid square data within specified bounds.

Uses a GeoJSON-like mapping for grid squares implementing the `__geo_interface__
<https://gist.github.com/sgillies/2217756>`__. Use of this protocol enables
integration with geospatial data processing libraries and tools.

Grid square data covering the BNG index system bounds is provided as an iterator at
100km, 50km, 10km, 5km and 1km resolutions. ``GeoPandas`` can be used to read the
iterator data directly into a ``GeoDataFrame`` for further processing using
`geopandas.GeoDataFrame.from_features()
<https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoDataFrame.from_features
.html>`__ or similar methods. Iterators can be converted to lists to generate all grid
square GeoJSON-like Features at a given resolution.
"""

from typing import Any, Iterator

from osbng.indexing import bbox_to_bng

__all__ = [
    "BNG_BOUNDS",
    "bbox_to_bng_iterfeatures",
    "bng_grid_100km",
    "bng_grid_50km",
    "bng_grid_10km",
    "bng_grid_5km",
    "bng_grid_1km",
]

# BNG index system bounds
BNG_BOUNDS = (0, 0, 700000, 1300000)


def bbox_to_bng_iterfeatures(
    xmin: int | float,
    ymin: int | float,
    xmax: int | float,
    ymax: int | float,
    resolution: int | str,
) -> Iterator[dict[str, Any]]:
    """Returns an iterator of BNGReference Features given a bounding box and resolution.

    Implements the `__geo_interface__
    <https://gist.github.com/sgillies/2217756>`__ protocol. The returned data structure
    represents the :class:`~osbng.bng_reference.BNGReference` object as a GeoJSON-like
    Feature.

    Args:
        xmin (int | float): The minimum easting coordinate of the bounding box (BBOX).
        ymin (int | float): The minimum northing coordinate of the BBOX.
        xmax (int | float): The maximum easting coordinate of the BBOX.
        ymax (int | float): The maximum northing coordinate of the BBOX.
        resolution (int | str): The BNG resolution expressed either as a metre-based
            integer or as a string label.

    Yields:
        dict[str, Any]: A GeoJSON-like representation of a BNGReference object.

    Raises:
        BNGResolutionError: If the resolution is not a valid resolution.
    """
    # Convert the bounding box to BNGReference objects
    bng_refs = bbox_to_bng(xmin, ymin, xmax, ymax, resolution)

    # Yield BNGReference object GeoJSON-like Features
    for bng_ref in bng_refs:
        yield bng_ref.__geo_interface__


# Grid square data covering the BNG index system bounds provided at
# 100km, 50km, 10km, 5km and 1km resolutions as iterators
# Iterators can be converted to a list to trigger generation of
# BNGReference object Features
# Resolution capped at 1km to prevent excessive data generation
# for lower (finer) resolutions
bng_grid_100km = bbox_to_bng_iterfeatures(*BNG_BOUNDS, "100km")
bng_grid_50km = bbox_to_bng_iterfeatures(*BNG_BOUNDS, "50km")
bng_grid_10km = bbox_to_bng_iterfeatures(*BNG_BOUNDS, "10km")
bng_grid_5km = bbox_to_bng_iterfeatures(*BNG_BOUNDS, "5km")
bng_grid_1km = bbox_to_bng_iterfeatures(*BNG_BOUNDS, "1km")
