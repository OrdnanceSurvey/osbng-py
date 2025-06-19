"""A Python package supporting geospatial grid indexing and interaction with Ordnance Survey's British National Grid index system."""

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
__version__ = "0.1.0"
