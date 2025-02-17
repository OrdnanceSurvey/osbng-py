"""Provides functionality to traverse the BNG grid system
"""

from shapely import distance
from osbng.indexing import bng_to_xy
from osbng.bng_reference import BNGReference, _validate_bngreference_pair
from shapely.geometry import Point
from osbng.errors import BNGNeighbourError


@_validate_bngreference_pair
def bng_distance(bng_ref1: BNGReference, bng_ref2: BNGReference) -> float:
    """Returns the euclidean distance between the centroids of two BNGReference objects.

    Args:
        bng_ref1 (BNGReference): A BNGReference object.
        bng_ref2 (BNGReference): A BNGReference object.

    Returns:
        float: The euclidean distance between the centroids of the two BNGReference objects.

    Raises:
        TypeError: If the first or second argument is not a BNGReference object.

    Examples:
        >>> bng_distance(BNGReference('SE1433'), BNGReference('SE1533'))
        1000.0
        >>> bng_distance(BNGReference('SE1433'), BNGReference('SE1631'))
        2828.42712474619
        >>> bng_distance(BNGReference('SE1433'), BNGReference('SE'))
        39147.158262126766
        >>> bng_distance(BNGReference('SE1433'), BNGReference('SENW'))
        42807.709586007986
        >>> bng_distance(BNGReference('SE'), BNGReference('OV'))
        141421.35623730952
    """

    # Derive the centroid of the first BNGReference object
    centroid1 = bng_to_xy(bng_ref1, "centre")

    # Derive the centroid of the second BNGReference object
    centroid2 = bng_to_xy(bng_ref2, "centre")

    # Return the distance between the two centroids
    return distance(Point(centroid1), Point(centroid2))
