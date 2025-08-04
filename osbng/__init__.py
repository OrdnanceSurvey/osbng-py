"""A Python package supporting Ordnance Survey's British National Grid index system.

This package enables the use of the BNG index system for geospatial grid indexing and
other interactions.
"""

from osbng.bng_reference import BNGReference
from osbng.grids import *
from osbng.indexing import xy_to_bng, bbox_to_bng, geom_to_bng, geom_to_bng_intersection
from osbng.resolution import BNG_RESOLUTIONS

__all__ = [
    "BNG_BOUNDS",
    "BNG_RESOLUTIONS",
    "BNGReference",
    "bng_grid_100km",
    "bng_grid_50km",
    "bng_grid_10km",
    "bng_grid_5km",
    "bng_grid_1km",
    "xy_to_bng",
    "bbox_to_bng",
    "bbox_to_bng_iterfeatures",
    "geom_to_bng",
    "geom_to_bng_intersection",
]
__version__ = "0.3.1"
