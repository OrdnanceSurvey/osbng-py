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
BNG_BOUNDS: tuple[int, int, int, int] = (0, 0, 700000, 1300000)
"""tuple[int, int, int, int]: BNG index system bounding box.

Expressed as (xmin, ymin, xmax, ymax) using easting and northing coordinates.

Represents the valid extent for :class:`~osbng.bng_reference.BNGReference` and grid 
generation.
"""


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

    Examples:
        >>> print(*bbox_to_bng_iterfeatures(530000, 180000, 535000, 185000, "5km"))
        {'type': 'Feature', 'properties': {'bng_ref': 'TQ38SW'}, 'geometry':
        {'type': 'Polygon', 'coordinates': (((535000.0, 180000.0), (535000.0, 185000.0),
        (530000.0, 185000.0), (530000.0, 180000.0), (535000.0, 180000.0)),)}}
        >>> print(*bbox_to_bng_iterfeatures(530000, 180000, 535000, 185000, "10km"))
        {'type': 'Feature', 'properties': {'bng_ref': 'TQ38'}, 'geometry':
        {'type': 'Polygon', 'coordinates': (((540000.0, 180000.0), (540000.0, 190000.0),
        (530000.0, 190000.0), (530000.0, 180000.0), (540000.0, 180000.0)),)}}

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

bng_grid_100km: Iterator[dict[str, Any]] = bbox_to_bng_iterfeatures(
    *BNG_BOUNDS, "100km"
)
"""Iterator of GeoJSON-like Features for 100km BNG grid squares within ``BNG_BOUNDS``.

Each yielded dictionary implements the ``__geo_interface__``  for a single 100km BNG 
grid square and corresponds to a :class:`~osbng.bng_reference.BNGReference` at 100 km 
resolution.

Notes:
    - No Features are generated until the iterator is consumed.
    - Convert to a list (``list(bng_grid_100km)``) to trigger Feature generation.
    - Pass directly to ``gpd.GeoDataFrame.from_features`` for ``GeoDataFrame`` 
      construction.
"""

bng_grid_50km: Iterator[dict[str, Any]] = bbox_to_bng_iterfeatures(*BNG_BOUNDS, "50km")
"""Iterator of GeoJSON-like Features for 50km BNG grid squares within ``BNG_BOUNDS``.

Each yielded dictionary implements the ``__geo_interface__``  for a single 50km BNG grid
square and corresponds to a :class:`~osbng.bng_reference.BNGReference` at 50km 
resolution.

Notes:
    - No Features are generated until the iterator is consumed.
    - Convert to a list (``list(bng_grid_50km)``) to trigger Feature generation.
    - Pass directly to ``gpd.GeoDataFrame.from_features`` for ``GeoDataFrame`` 
      construction.
"""

bng_grid_10km: Iterator[dict[str, Any]] = bbox_to_bng_iterfeatures(*BNG_BOUNDS, "10km")
"""Iterator of GeoJSON-like Features for 10km BNG grid squares within ``BNG_BOUNDS``.

Each yielded dictionary implements the ``__geo_interface__``  for a single 10km BNG grid
square and corresponds to a :class:`~osbng.bng_reference.BNGReference` at 10km 
resolution.

Notes:
    - No Features are generated until the iterator is consumed.
    - Convert to a list (``list(bng_grid_10km)``) to trigger Feature generation.
    - Pass directly to ``gpd.GeoDataFrame.from_features`` for ``GeoDataFrame`` 
      construction.
"""

bng_grid_5km: Iterator[dict[str, Any]] = bbox_to_bng_iterfeatures(*BNG_BOUNDS, "5km")
"""Iterator of GeoJSON-like Features for all 5km BNG grid squares within ``BNG_BOUNDS``.

Each yielded dictionary implements the ``__geo_interface__``  for a single 5km BNG grid 
square and corresponds to a :class:`~osbng.bng_reference.BNGReference` at 5km resolution
.

Notes:
    - No Features are generated until the iterator is consumed.
    - Convert to a list (``list(bng_grid_5km)``) to trigger Feature generation.
    - Pass directly to ``gpd.GeoDataFrame.from_features`` for ``GeoDataFrame`` 
      construction.
"""

bng_grid_1km: Iterator[dict[str, Any]] = bbox_to_bng_iterfeatures(*BNG_BOUNDS, "1km")
"""Iterator of GeoJSON-like Features for all 1km BNG grid squares within ``BNG_BOUNDS``.

Each yielded dictionary implements the ``__geo_interface__``  for a single 1km BNG grid 
square and corresponds to a :class:`~osbng.bng_reference.BNGReference` at 1km resolution
.

Notes:
    - No Features are generated until the iterator is consumed.
    - Convert to a list (``list(bng_grid_1km)``) to trigger Feature generation.
    - Pass directly to ``gpd.GeoDataFrame.from_features`` for ``GeoDataFrame`` 
      construction.
"""
