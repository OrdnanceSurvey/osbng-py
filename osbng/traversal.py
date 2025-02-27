"""Provides functionality for traversing and calculating distances within the British National Grid (BNG) index system.

It supports spatial analyses such as distance-constrained nearest neighbour searches and 'distance within' queries by offering:
- **Grid traversal**: Generate k-discs and k-rings around a given grid square.
- **Neighbourhood operations**: Identify neighbouring grid squares and checking adjacency.
- **Distance computation**: Calculate the distance between grid square centroids.
- **Proximity queries**: Retrieve all grid squares within a specified absolute distance.
 
"""

from shapely import distance
from osbng.indexing import bng_to_xy
from osbng.bng_reference import BNGReference, _validate_bngreference, _validate_bngreference_pair
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


@_validate_bngreference_pair
def bng_is_neighbour(bng_ref1: BNGReference, bng_ref2: BNGReference) -> bool:
    """Returns True if the two BNGReference objects are neighbours, otherwise False.
    Neighbours are defined as grid squares that share an edge with the first BNGReference object.

    Args:
        bng_ref1 (BNGReference): A BNGReference object.
        bng_ref2 (BNGReference): A BNGReference object.

    Returns:
        bool: True if the two BNGReference objects are neighbours, otherwise False.

    Raises:
        TypeError: If the first or second argument is not a BNGReference object.
        BNGNeighbourError: If the two BNGReference objects are not at the same resolution.
        BNGNeighbourError: If the two BNGReference objects are the same.

    Examples:
        >>> bng_is_neighbour(BNGReference("SE1921"), BNGReference("SE1821"))
        True
        >>> bng_is_neighbour(BNGReference("SE1922"), BNGReference("SE1821"))
        False

    """

    # Check if the two BNGReference objects are at the same resolution
    if bng_ref1.resolution_metres != bng_ref2.resolution_metres:
        raise BNGNeighbourError(
            "The input BNG Resolution objects are not the same grid resolution. The input BNG Resolution objects must be the same grid resolution."
        )
    # Check if the two BNGReference objects are the same
    elif bng_ref1 == bng_ref2:
        raise BNGNeighbourError(
            "The input BNG Resolution objects are the same. The input BNG Resolution objects must be different."
        )
    # Otherwise check if the two BNGReference objects are neighbours
    else:

        # Get the x and y coordinates of the centroid of the first BNGReference object
        x, y = bng_to_xy(bng_ref1, "centre")

        # Get the resolution of the first BNGReference object
        resolution = bng_ref1.resolution_metres

        # Add the resolution to the easting and northing to get the centroid of the four neighbouring grid cells
        north = (x, y + resolution)
        east = (x + resolution, y)
        south = (x, y - resolution)
        west = (x - resolution, y)

        # Get the centroid of the second BNGReference object
        centroid = bng_to_xy(bng_ref2, "centre")

        # Check if the centroid of the second BNGReference object equals any of the four neighbouring grid cell centroids of the first BNGReference object
        if centroid in [north, east, south, west]:
            return True
        else:
            return False
