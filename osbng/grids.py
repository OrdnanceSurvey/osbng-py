"""Provides functionality to generate British National Grid (BNG) grid square data within specified bounds.

Uses a GeoJSON-like mapping for grid squares implementing the __geo_interface__ protocol (https://gist.github.com/sgillies/2217756).
Use of this protocol enables integration with geospatial data processing libraries and tools.

Grid square data covering the BNG index system bounds is provided at 100km, 50km, 10km and 5km resolutions.
"""

from typing import Iterator, Union

from osbng.indexing import bbox_to_bng

__all__ = [
    "BNG_BOUNDS",
    "bbox_to_bng_iterfeatures",
    "bng_grid_100km",
    "bng_grid_50km",
    "bng_grid_10km",
    "bng_grid_5km",
]

# BNG index system bounds
BNG_BOUNDS = (0, 0, 700000, 1300000)


def bbox_to_bng_iterfeatures(
    xmin: float, ymin: float, xmax: float, ymax: float, resolution: int | str
) -> Iterator[dict[str, Union[str, dict]]]:
    """Returns an iterator of BNGReference objects represented using a GeoJSON-like 
       mapping within specified bounds at a specified resolution.

    Implements the __geo_interface__ protocol. The returned data structure represents 
    the BNGReference object as a GeoJSON-like Feature.

    Args:
        xmin (float): The minimum x-coordinate of the bounding box.
        ymin (float): The minimum y-coordinate of the bounding box.
        xmax (float): The maximum x-coordinate of the bounding box.
        ymax (float): The maximum y-coordinate of the bounding box.
        resolution (int | str): The BNG resolution expressed either as a metre-based integer or as a string label.

    Yields:
        dict: A GeoJSON-like representation of a BNGReference object.

    Raises:
        BNGResolutionError: If the resolution is not a valid resolution.
    """
    # Convert the bounding box to BNGReference objects
    bng_refs = bbox_to_bng(xmin, ymin, xmax, ymax, resolution)

    # Yield BNGReference object GeoJSON-like Features
    for bng_ref in bng_refs:
        yield bng_ref.__geo_interface__


# Generate BNGReference object Features covering the BNG index system bounds 
# Grid square data provided at 100km, 50km, 10km and 5km resolutions
# Resolution capped at 5km to prevent excessive data generation
bng_grid_100km = list(bbox_to_bng_iterfeatures(*BNG_BOUNDS, "100km"))
bng_grid_50km = list(bbox_to_bng_iterfeatures(*BNG_BOUNDS, "50km"))
bng_grid_10km = list(bbox_to_bng_iterfeatures(*BNG_BOUNDS, "10km"))
bng_grid_5km = list(bbox_to_bng_iterfeatures(*BNG_BOUNDS, "5km"))
