"""Provides functionality for traversing and calculating distances within the British National Grid (BNG) index system.

It supports spatial analyses such as distance-constrained nearest neighbour searches and 'distance within' queries by offering:
- **Grid traversal**: Generate k-discs and k-rings around a given grid square.
- **Neighbourhood operations**: Identify neighbouring grid squares and checking adjacency.
- **Distance computation**: Calculate the distance between grid square centroids.
- **Proximity queries**: Retrieve all grid squares within a specified absolute distance.
 
"""

import numpy as np
import warnings

from osbng.indexing import bng_to_xy, xy_to_bng
from osbng.bng_reference import BNGReference, _validate_bngreference, _validate_bngreference_pair
from osbng.errors import BNGExtentError, BNGNeighbourError

__all__ = [
    "bng_kring",
    "bng_kdisc",
    "bng_distance",
    "bng_neighbours",
    "bng_is_neighbour",
    "bng_dwithin",
]

def _ring_or_disc_(bng_ref: BNGReference, k: int, is_disc: bool) -> list[BNGReference]:
    """Helper function to extract grid squares in a disc or ring.

    Args:
        bng_ref (BNGReference): A BNGReference object.
        k (int): Grid distance in units of grid squares.
        is_disc (bool): If True, returns all grid squares within distance k.  If False, only returns the outer ring.

    Returns:
        list of BNGReference: All BNGReference objects representing grid squares in a square ring or disc of radius k.
    """
    
    # Check that k is a positive integer
    if k<=0:
        raise ValueError(
            "k must be a positive integer."
        )
    
    
    # Derive point location of root square
    xc, yc = bng_to_xy(bng_ref, "centre")

    # Initialise list of ring BNG reference objects
    kring_refs = []

    # Track whether we need to raise an extent warning
    raise_extent_warning = False

    # Iterate over all dx/dy within range
    for dy in range(-k,k+1):
        for dx in range(-k,k+1):
            # Include all dx/dy combinations for disks
            # Only include edges for rings
            if is_disc | (abs(dy)==k) | (abs(dx)==k):
                try:
                    ring_ref = xy_to_bng(
                        xc+(dx*bng_ref.resolution_metres),
                        yc+(dy*bng_ref.resolution_metres),
                        bng_ref.resolution_metres
                    )
                # Catch extent errors and track whether warning is needed
                except BNGExtentError:
                    raise_extent_warning = True
                else:
                    kring_refs.append(ring_ref)

    # Raise an extent warning if an error has been caught
    # Note: do this after the above, otherwise repeated warnings will be raised!
    if raise_extent_warning:
        warnings.warn(
            "One or more of the requested grid squares falls outside of the BNG index "
            +"system extent and will not be returned."
        )

    return kring_refs

@_validate_bngreference
def bng_kring(bng_ref: BNGReference, k: int) -> list[BNGReference]:
    """Returns a list of BNG reference objects representing a hollow ring around a given grid square
    at a grid distance k.

    Args:
        bng_ref (BNGReference): A BNGReference object.
        k (int): Grid distance in units of grid squares.

    Returns:
        list of BNGReference: All BNGReference objects representing squares in a square ring of radius k.

    Examples:
        >>> bng_kring(BNGReference('SU1234'), 1)
        [BNGReference('SU1133'), BNGReference('SU1233'), BNGReference('SU1333'), BNGReference('SU1134'),
        BNGReference('SU1334'), BNGReference('SU1135'), BNGReference('SU1235'), BNGReference('SU1335')]
        >>> bng_kring(BNGReference('SU1234'), 3)
        [list of 24 BNGReference objects]
    """

    return _ring_or_disc_(bng_ref, k, False)

@_validate_bngreference
def bng_kdisc(bng_ref: BNGReference, k: int) -> list[BNGReference]:
    """Returns a list of BNG reference objects representing a filled disc around a given grid square
    up to a grid distance k, including the given central grid square.

    Args:
        bng_ref (BNGReference): A BNGReference object.
        k (int): Grid distance in units of grid squares.

    Returns:
        list of BNGReference: All BNGReference objects representing grid squares in a square of radius k.

    Examples:
        >>> bng_kdisc(BNGReference('SU1234'), 1)
        [BNGReference('SU1133'), BNGReference('SU1233'), BNGReference('SU1333'), BNGReference('SU1134'),
        BNGReference('SU1234'), BNGReference('SU1334'), BNGReference('SU1135'), BNGReference('SU1235'),
        BNGReference('SU1335')]
        >>> bng_kdisc(BNGReference('SU1234'), 3)
        [list of 49 BNGReference objects]
    """

    return _ring_or_disc_(bng_ref, k, True)


@_validate_bngreference_pair
def bng_distance(bng_ref1: BNGReference, bng_ref2: BNGReference, edge_to_edge: bool = False) -> float:
    """Returns the euclidean distance between the centroids of two BNGReference objects.

    Args:
        bng_ref1 (BNGReference): A BNGReference object.
        bng_ref2 (BNGReference): A BNGReference object.

    Kwargs:
        edge_to_edge (bool): If False (default), distance will be centroid-to-centroid distance.
            If True, distance will be the shortest distance between any point in the grid squares.

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

    if edge_to_edge:       
        
        # For edge-to-edge distances, the x-distance and y-distance are the centroid-to-centroid
        # distance minus half the box width/height at either end
        dx = 0 if centroid1[0]==centroid2[0] else abs(centroid1[0]-centroid2[0])-0.5*(bng_ref1.resolution_metres+bng_ref2.resolution_metres)
        dy = 0 if centroid1[1]==centroid2[1] else abs(centroid1[1]-centroid2[1])-0.5*(bng_ref1.resolution_metres+bng_ref2.resolution_metres)

    else:
        dx = centroid1[0]-centroid2[0]
        dy = centroid1[1]-centroid2[1]

    return float(np.sqrt(dx**2 + dy**2))


@_validate_bngreference
def bng_neighbours(bng_ref: BNGReference) -> list[BNGReference]:
    """Returns a list of BNGReference objects representing the four neighbouring grid squares
    sharing an edge with the input BNGReference.

    Args:
        bng_ref (BNGReference): A BNGReference object.

    Returns:
        list of BNGReference: The grid grid squares immediately North, South, East and West of bng_ref.

    Examples:
        >>> bng_neighbours(BNGReference('SU1234'))
        [BNGReference('SU1235'), BNGReference('SU1334'), BNGReference('SU1233'), BNGReference('SU1134')]
    """

    # Get the centroid of the bng square
    x, y = bng_to_xy(bng_ref, "centre")
    
    # Initialise a neighbours list
    neighbours_list = []

    # Track whether we need to raise an extent warning
    raise_extent_warning = False

    # Iterate through N,E,S,W neighbours
    for dx,dy in [[0,1], [1,0], [0,-1], [-1,0]]:
        try:
            neighbour = xy_to_bng(
                x+(dx*bng_ref.resolution_metres),
                y+(dy*bng_ref.resolution_metres),
                bng_ref.resolution_metres
            )
        # Catch extent errors and track whether we need to warn
        except BNGExtentError:
            raise_extent_warning = True
        else:
            neighbours_list.append(neighbour)

    # Raise an extent warning if an error has been caught
    # Note: do this after the above, otherwise repeated warnings will be raised!
    if raise_extent_warning:
        warnings.warn(
            "One or more of the requested grid squares falls outside of the BNG index "
            +"system extent and will not be returned."
        )

    return neighbours_list

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

    Examples:
        >>> bng_is_neighbour(BNGReference("SE1921"), BNGReference("SE1821"))
        True
        >>> bng_is_neighbour(BNGReference("SE1922"), BNGReference("SE1821"))
        False
        >>> bng_is_neighbour(BNGReference('SU1234'), BNGReference('SU1234'))
        False

    """

    # Check if the two BNGReference objects are at the same resolution
    if bng_ref1.resolution_metres != bng_ref2.resolution_metres:
        raise BNGNeighbourError(
            "The input BNG Resolution objects are not the same grid resolution. The input BNG Resolution objects must be the same grid resolution."
        )
    # Otherwise check if the two BNGReference objects are neighbours
    else:
        return bng_ref2 in bng_neighbours(bng_ref1)
    

@_validate_bngreference
def bng_dwithin(bng_ref: BNGReference, d: int | float) -> list[BNGReference]:
    """Returns a list of BNG reference objects around a given grid square within an absolute distance d.
    All squares will be returned for which any part of its boundary is within distance d of any part of
    bng_ref's boundary.

    Args:
        bng_ref (BNGReference): A BNGReference object.
        d (int or float): The absolute distance d in metres.

    Returns:
        list of BNGReference: All grid squares which have any part of their geometry within distance
            d of bng_ref's geometry

    Examples:
        >>> bng_dwithin(BNGReference('SU1234'), 1000)
        [BNGReference('SU1133'), BNGReference('SU1233'), BNGReference('SU1333'), BNGReference('SU1134'),
        BNGReference('SU1234'), BNGReference('SU1334'), BNGReference('SU1135'), BNGReference('SU1235'),
        BNGReference('SU1335')]
        >>> bng_dwithin(BNGReference('SU1234'), 1001)
        [list of 21 BNGReference objects]
    """

    # Convert distance to units of k
    k = int(np.ceil(d/bng_ref.resolution_metres))

    # Get full kdisc
    disc_refs = bng_kdisc(bng_ref, k) 

    # Return only those whose centroids are within distance
    return [r for r in disc_refs if bng_distance(bng_ref, r, edge_to_edge=True)<=d]
