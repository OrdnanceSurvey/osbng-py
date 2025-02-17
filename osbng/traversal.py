"""Provides functionality to traverse the BNG grid system
"""

from shapely import distance
from osbng.indexing import bng_to_xy
from osbng.bng_reference import BNGReference, _validate_bngreference_pair
from shapely.geometry import Point
from osbng.errors import BNGNeighbourError
