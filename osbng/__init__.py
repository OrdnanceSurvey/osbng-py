"""Geospatial grid indexing and interaction with the British National Grid.

Offers a streamlined programmatic interface to Ordnance Survey's British National Grid
(BNG) index system, enabling efficient spatial indexing and analysis based on grid
references. It supports a range of geospatial applications, including statistical
aggregation, data visualisation, and interoperability across datasets. Designed for
developers and analysts working with geospatial data in Great Britain, osbng simplifies
integration with geospatial workflows and provides intuitive tools for exploring the
structure and logic of the BNG system.
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
