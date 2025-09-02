"""Provides functionality for traversing the British National Grid (BNG) index system.

It supports spatial analyses such as distance-constrained nearest neighbour searches and
'distance within' queries by offering:

- **Grid traversal**: Generate k-discs and k-rings around a given grid square.
- **Neighbourhood operations**: Identify neighbouring grid squares and checking
  adjacency.
- **Distance computation**: Calculate the distance between grid square centroids.
- **Proximity queries**: Retrieve all grid squares within a specified absolute
  distance.

"""

import warnings

import numpy as np

from osbng.bng_reference import BNGReference, _validate_bngreferences
from osbng.errors import BNGExtentError, BNGNeighbourError
from osbng.hierarchy import bng_to_parent
from osbng.indexing import bng_to_xy, xy_to_bng

__all__ = [
    "bng_kring",
    "bng_kdisc",
    "bng_distance",
    "bng_neighbours",
    "bng_is_neighbour",
    "bng_dwithin",
]


def _ring_or_disc(
    bng_ref: BNGReference, k: int, is_disc: bool, return_relations: bool
) -> list[BNGReference] | list[(BNGReference, int, int)]:
    """Helper function to extract grid squares in a disc or ring.

    Args:
        bng_ref (BNGReference): A BNGReference object.
        k (int): Grid distance in units of grid squares.
        is_disc (bool): If True, returns all grid squares within distance k.  If False,
            only returns the outer ring.
        return_relations (bool): If True, returns a list of (BNGReference, dx, dy)
            tuples where dx, dy are integer offsets in grid units.  If False, returns a
            list of BNGReference objects.

    Returns:
        if return_relations==True:
            list[(BNGReference, dx, dy)]: All BNGReference objects representing grid
                squares in a square ring or disc of radius k, with the x- and y-offsets
                (in grid square units) between bng_ref and each returned BNGReference.
        else:
            list[BNGReference]: All BNGReference objects representing grid squares in a
                square ring or disc of radius k.
    """
    # Check that k is a positive integer
    if k <= 0:
        raise ValueError("k must be a positive integer.")

    # Derive point location of root square
    xc, yc = bng_to_xy(bng_ref, position="centre")

    # Initialise list of ring BNG reference objects
    kring_refs = []

    # Track whether we need to raise an extent warning
    raise_extent_warning = False

    # Iterate over all dx/dy within range
    for dy in range(-k, k + 1)[::-1]:
        for dx in range(-k, k + 1):
            # Include all dx/dy combinations for disks
            # Only include edges for rings
            if is_disc | (abs(dy) == k) | (abs(dx) == k):
                try:
                    ring_ref = xy_to_bng(
                        xc + (dx * bng_ref.resolution_metres),
                        yc + (dy * bng_ref.resolution_metres),
                        bng_ref.resolution_metres,
                    )
                # Catch extent errors and track whether warning is needed
                except BNGExtentError:
                    raise_extent_warning = True
                else:
                    kring_refs.append(
                        (ring_ref, dx, dy)
                    ) if return_relations else kring_refs.append(ring_ref)

    # Raise an extent warning if an error has been caught
    # Note: do this after the above, otherwise repeated warnings will be raised!
    if raise_extent_warning:
        warnings.warn(
            "One or more of the requested grid squares falls outside of the BNG index "
            + "system extent and will not be returned."
        )

    return kring_refs


@_validate_bngreferences
def bng_kring(
    bng_ref: BNGReference, k: int, *, return_relations: bool = False
) -> list[BNGReference] | list[tuple[BNGReference, int, int]]:
    """Returns a hollow ring of BNGReference objects around a ``BNGReference`` object.

    Returns all :class:`~osbng.bng_reference.BNGReference` objects at a grid distance
    ``k``.

    Notes:
        Returned :class:`~osbng.bng_reference.BNGReference` objects are ordered North to
        South then West to East, therefore not in ring order.

    Args:
        bng_ref (BNGReference): A :class:`~osbng.bng_reference.BNGReference` object.
        k (int): Grid distance in units of grid squares.

    Keyword Args:
        return_relations (bool, optional): If True, returns a list of
            (:class:`~osbng.bng_reference.BNGReference`, dx, dy) tuples where dx, dy are
            integer offsets in grid units.  If False (default), returns a list of
            :class:`~osbng.bng_reference.BNGReference` objects.  Keyword only.

    Returns:
        list[BNGReference]: If ``return_relations`` is False (default), returns all
        :class:`~osbng.bng_reference.BNGReference` objects representing squares in a
        square ring of radius ``k``.
        If ``return_relations`` is True, returns a list of
        (:class:`~osbng.bng_reference.BNGReference`, dx, dy) tuples, where dx and dy are
        the x and y offsets between ``bng_ref`` and each returned
        :class:`~osbng.bng_reference.BNGReference` object in units of grid squares.

    Examples:
        >>> bng_kring(BNGReference("SU1234"), 1)
        [
        BNGReference(bng_ref_formatted=SU 11 35, resolution_label=1km),
        BNGReference(bng_ref_formatted=SU 12 35, resolution_label=1km),
        BNGReference(bng_ref_formatted=SU 13 35, resolution_label=1km),
        BNGReference(bng_ref_formatted=SU 11 34, resolution_label=1km),
        BNGReference(bng_ref_formatted=SU 13 34, resolution_label=1km),
        BNGReference(bng_ref_formatted=SU 11 33, resolution_label=1km),
        BNGReference(bng_ref_formatted=SU 12 33, resolution_label=1km),
        BNGReference(bng_ref_formatted=SU 13 33, resolution_label=1km)
        ]
        >>> bng_kring(BNGReference("SU1234"), 1, return_relations=True)
        [(BNGReference(bng_ref_formatted=SU 11 35, resolution_label=1km), -1, 1),
        (BNGReference(bng_ref_formatted=SU 12 35, resolution_label=1km), 0, 1),
        (BNGReference(bng_ref_formatted=SU 13 35, resolution_label=1km), 1, 1),
        (BNGReference(bng_ref_formatted=SU 11 34, resolution_label=1km), -1, 0),
        (BNGReference(bng_ref_formatted=SU 13 34, resolution_label=1km), 1, 0),
        (BNGReference(bng_ref_formatted=SU 11 33, resolution_label=1km), -1, -1),
        (BNGReference(bng_ref_formatted=SU 12 33, resolution_label=1km), 0, -1),
        (BNGReference(bng_ref_formatted=SU 13 33, resolution_label=1km), 1, -1)]
        >>> bng_kring(BNGReference("SU1234"), 3)
        [list of 24 BNGReference objects]

    See Also:
        - The equivalent :meth:`osbng.bng_reference.BNGReference.bng_kring` instance
          method.
        - The :func:`~osbng.traversal.bng_kdisc` function and
          :meth:`osbng.bng_reference.BNGReference.bng_kdisc` instance method for
          finding all :class:`~osbng.bng_reference.BNGReference` objects within a
          distance d from an input :class:`~osbng.bng_reference.BNGReference` object.
    """
    return _ring_or_disc(bng_ref, k, False, return_relations)


@_validate_bngreferences
def bng_kdisc(
    bng_ref: BNGReference, k: int, *, return_relations: bool = False
) -> list[BNGReference] | list[tuple[BNGReference, int, int]]:
    """Returns a filled disc of BNGReference objects around a ``BNGReference``.

    Returns all :class:`~osbng.bng_reference.BNGReference` objects up to a grid
    distance ``k``, including the given central
    :class:`~osbng.bng_reference.BNGReference` object.

    Notes:
        Returned :class:`~osbng.bng_reference.BNGReference` objects are ordered North to
        South then West to East.

    Args:
        bng_ref (BNGReference): A :class:`~osbng.bng_reference.BNGReference` object.
        k (int): Grid distance in units of grid squares.

    Keyword Args:
        return_relations (bool, optional): If True, returns a list of
            (:class:`~osbng.bng_reference.BNGReference`, dx, dy) tuples where dx, dy are
            integer offsets in grid units.  If False (default), returns a list of
            :class:`~osbng.bng_reference.BNGReference` objects. Keyword only.

    Returns:
        list[BNGReference]: If ``return_relations`` is False (default), returns all
        :class:`~osbng.bng_reference.BNGReference` objects representing grid squares in
        a square ring of radius k.
        If ``return_relations`` is True, returns a list of
        (:class:`~osbng.bng_reference.BNGReference`, dx, dy) tuples, where dx and dy are
        the x and y offsets between ``bng_ref`` and each returned
        :class:`~osbng.bng_reference.BNGReference` object in units of grid squares.

    Examples:
        >>> bng_kdisc(BNGReference("SU1234"), 1)
        [
        BNGReference(bng_ref_formatted=SU 11 35, resolution_label=1km),
        BNGReference(bng_ref_formatted=SU 12 35, resolution_label=1km),
        BNGReference(bng_ref_formatted=SU 13 35, resolution_label=1km),
        BNGReference(bng_ref_formatted=SU 11 34, resolution_label=1km),
        BNGReference(bng_ref_formatted=SU 12 34, resolution_label=1km),
        BNGReference(bng_ref_formatted=SU 13 34, resolution_label=1km),
        BNGReference(bng_ref_formatted=SU 11 33, resolution_label=1km),
        BNGReference(bng_ref_formatted=SU 12 33, resolution_label=1km),
        BNGReference(bng_ref_formatted=SU 13 33, resolution_label=1km)
        ]
        >>> bng_kdisc(BNGReference("SU1234"), 1, return_relations=True)
        [(BNGReference(bng_ref_formatted=SU 11 35, resolution_label=1km), -1, 1),
        (BNGReference(bng_ref_formatted=SU 12 35, resolution_label=1km), 0, 1),
        (BNGReference(bng_ref_formatted=SU 13 35, resolution_label=1km), 1, 1),
        (BNGReference(bng_ref_formatted=SU 11 34, resolution_label=1km), -1, 0),
        (BNGReference(bng_ref_formatted=SU 12 34, resolution_label=1km), 0, 0),
        (BNGReference(bng_ref_formatted=SU 13 34, resolution_label=1km), 1, 0),
        (BNGReference(bng_ref_formatted=SU 11 33, resolution_label=1km), -1, -1),
        (BNGReference(bng_ref_formatted=SU 12 33, resolution_label=1km), 0, -1),
        (BNGReference(bng_ref_formatted=SU 13 33, resolution_label=1km), 1, -1)]
        >>> bng_kdisc(BNGReference("SU1234"), 3)
        [list of 49 BNGReference objects]

    See Also:
        - The equivalent :meth:`osbng.bng_reference.BNGReference.bng_kdisc` instance
          method.
        - The :func:`~osbng.traversal.bng_kring` function and
          :meth:`osbng.bng_reference.BNGReference.bng_kring` instance method for
          finding all :class:`~osbng.bng_reference.BNGReference` objects at a
          specific distance d from an input
          :class:`~osbng.bng_reference.BNGReference` object.
    """
    return _ring_or_disc(bng_ref, k, True, return_relations)


@_validate_bngreferences
def bng_distance(
    bng_ref1: BNGReference, bng_ref2: BNGReference, *, edge_to_edge: bool = False
) -> float:
    """Returns the euclidean distance between two ``BNGReference`` objects.

    When ``edge_to_edge`` is False, the distance is the centroid-to-centroid distance in
    metres.  When ``edge_to_edge`` is True, the distance is the shortest distance
    between any two parts of the grid squares.

    Notes:
        Note that the two :class:`~osbng.bng_reference.BNGReference` objects do not
        necessarily need to share a common resolution.  When ``edge_to_edge`` = True and
        ``bng_ref1`` and ``bng_ref2`` have a parent-child relationship, the returned
        distance is 0.

    Args:
        bng_ref1 (BNGReference): A :class:`~osbng.bng_reference.BNGReference` object.
        bng_ref2 (BNGReference): A :class:`~osbng.bng_reference.BNGReference` object.

    Keyword Args:
        edge_to_edge (bool, optional): If False (default), distance will be
            centroid-to-centroid distance.  If True, distance will be the shortest
            distance between any point in the grid squares.  Keyword only.

    Returns:
        float: The euclidean distance between the two
        :class:`~osbng.bng_reference.BNGReference` objects.

    Raises:
        TypeError: If the first or second argument is not a
            :class:`~osbng.bng_reference.BNGReference` object.

    Examples:
        >>> bng_distance(BNGReference("SE1433"), BNGReference("SE1533"))
        1000.0
        >>> bng_distance(
        ...     BNGReference("SE1433"), BNGReference("SE1533"), edge_to_edge=True
        ... )
        0.0
        >>> bng_distance(BNGReference("SE1433"), BNGReference("SE1631"))
        2828.42712474619
        >>> bng_distance(BNGReference("SE1433"), BNGReference("SE"))
        39147.158262126766
        >>> bng_distance(BNGReference("SE1433"), BNGReference("SENW"))
        42807.709586007986
        >>> bng_distance(BNGReference("SE"), BNGReference("OV"))
        141421.35623730952
        >>> bng_distance(BNGReference("SU"), BNGReference("SU2345"), edge_to_edge=True)
        0.0

    See Also:
        - The equivalent :meth:`osbng.bng_reference.BNGReference.bng_distance` instance
          method.
        - The :func:`~osbng.traversal.bng_dwithin` function and
          :meth:`osbng.bng_reference.BNGReference.bng_dwithin` instance method for
          obtaining all :class:`~osbng.bng_reference.BNGReference` objects within a
          defined distance of an input :class:`~osbng.bng_reference.BNGReference`
          object.
    """
    # Catch the special case of parent-child relationship when using edge-to-edge
    if (bng_ref1.resolution_metres != bng_ref2.resolution_metres) & edge_to_edge:
        # Identify the possible parent and child
        # Note this is required, to avoid errors by testing bng_to_parent on a
        # BNGReference with resolution of 100km!
        parent_candidate, child_candidate = (
            (bng_ref1, bng_ref2)
            if bng_ref1.resolution_metres > bng_ref2.resolution_metres
            else (bng_ref2, bng_ref1)
        )

        # Return distance of 0 if one is a parent of the other
        if (
            bng_to_parent(
                child_candidate, resolution=parent_candidate.resolution_metres
            )
            == parent_candidate
        ):
            return 0.0

    # Derive the centroid of the first BNGReference object
    centroid1 = bng_to_xy(bng_ref1, position="centre")

    # Derive the centroid of the second BNGReference object
    centroid2 = bng_to_xy(bng_ref2, position="centre")

    # Note this must be a new if-else logic to the above special case, to catch cases
    # where bng_ref1 and bng_ref2 do not share a resolution but are not parents
    if edge_to_edge:
        # For edge-to-edge distances, the x-distance and y-distance are the
        # centroid-to-centroid distance minus half the box width/height at either end
        dx = (
            0
            if centroid1[0] == centroid2[0]
            else abs(centroid1[0] - centroid2[0])
            - 0.5 * (bng_ref1.resolution_metres + bng_ref2.resolution_metres)
        )
        dy = (
            0
            if centroid1[1] == centroid2[1]
            else abs(centroid1[1] - centroid2[1])
            - 0.5 * (bng_ref1.resolution_metres + bng_ref2.resolution_metres)
        )

    else:
        dx = centroid1[0] - centroid2[0]
        dy = centroid1[1] - centroid2[1]

    return float(np.sqrt(dx**2 + dy**2))


@_validate_bngreferences
def bng_neighbours(bng_ref: BNGReference) -> list[BNGReference]:
    """Returns the four ``BNGReference`` object neighbours of a ``BNGReference``.

    The neighbours are defined as the grid squares immediately North, East, South and
    West of the input grid square sharing an edge with the input
    :class:`~osbng.bng_reference.BNGReference` object.

    Args:
        bng_ref (BNGReference): A :class:`~osbng.bng_reference.BNGReference` object.

    Returns:
        list[BNGReference]: The grid squares immediately North, East, South and West
        of bng_ref, in that order.

    Examples:
        >>> bng_neighbours(BNGReference("SU1234"))
        [
        BNGReference(bng_ref_formatted=SU 12 35, resolution_label=1km),
        BNGReference(bng_ref_formatted=SU 13 34, resolution_label=1km),
        BNGReference(bng_ref_formatted=SU 12 33, resolution_label=1km),
        BNGReference(bng_ref_formatted=SU 11 34, resolution_label=1km)
        ]

    See Also:
        - The equivalent :meth:`osbng.bng_reference.BNGReference.bng_neighbours`
          instance method.
        - The :func:`~osbng.traversal.bng_is_neighbour` function and
          :meth:`osbng.bng_reference.BNGReference.bng_is_neighbour` instance method for
          testing whether two :class:`~osbng.bng_reference.BNGReference` objects are
          neighbours.
    """
    # Get the centroid of the bng square
    x, y = bng_to_xy(bng_ref, position="centre")

    # Initialise a neighbours list
    neighbours_list = []

    # Track whether we need to raise an extent warning
    raise_extent_warning = False

    # Iterate through N,E,S,W neighbours
    for dx, dy in [[0, 1], [1, 0], [0, -1], [-1, 0]]:
        try:
            neighbour = xy_to_bng(
                x + (dx * bng_ref.resolution_metres),
                y + (dy * bng_ref.resolution_metres),
                bng_ref.resolution_metres,
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
            + "system extent and will not be returned."
        )

    return neighbours_list


@_validate_bngreferences
def bng_is_neighbour(bng_ref1: BNGReference, bng_ref2: BNGReference) -> bool:
    """Tests whether two ``BNGReference`` objects are neighbours.

    Returns True if the two :class:`~osbng.bng_reference.BNGReference` objects are
    neighbours, otherwise False.  Neighbours are defined as grid squares that share an
    edge with the first :class:`~osbng.bng_reference.BNGReference` object.

    Args:
        bng_ref1 (BNGReference): A :class:`~osbng.bng_reference.BNGReference` object.
        bng_ref2 (BNGReference): A :class:`~osbng.bng_reference.BNGReference` object.

    Returns:
        bool: True if the two :class:`~osbng.bng_reference.BNGReference` objects are
        neighbours, otherwise False.

    Raises:
        TypeError: If the first or second argument is not a
            :class:`~osbng.bng_reference.BNGReference` object.
        BNGNeighbourError: If the two :class:`~osbng.bng_reference.BNGReference`
            objects are not at the same resolution.

    Examples:
        >>> bng_is_neighbour(BNGReference("SE1921"), BNGReference("SE1821"))
        True
        >>> bng_is_neighbour(BNGReference("SE1922"), BNGReference("SE1821"))
        False
        >>> bng_is_neighbour(BNGReference("SU1234"), BNGReference("SU1234"))
        False

    See Also:
        - The equivalent :meth:`osbng.bng_reference.BNGReference.bng_is_neighbour`
          instance method.
        - The :func:`~osbng.traversal.bng_neighbours` function and
          :meth:`osbng.bng_reference.BNGReference.bng_neighbours` instance method for
          obtaining all neighbouring :class:`~osbng.bng_reference.BNGReference` objects
          of an input :class:`~osbng.bng_reference.BNGReference` object.

    """
    # Check if the two BNGReference objects are at the same resolution
    if bng_ref1.resolution_metres != bng_ref2.resolution_metres:
        raise BNGNeighbourError(
            "The input BNGReference objects are not the same grid resolution."
            "The inputBNGReference objects must be the same grid resolution."
        )
    # Otherwise check if the two BNGReference objects are neighbours
    else:
        return bng_ref2 in bng_neighbours(bng_ref1)


@_validate_bngreferences
def bng_dwithin(bng_ref: BNGReference, d: int | float) -> list[BNGReference]:
    """Returns a list of ``BNGReference`` objects within an absolute distance ``d``.

    All squares will be returned for which any part of its boundary is within distance
    ``d`` of any part of the input :class:`~osbng.bng_reference.BNGReference`'s
    boundary.

    Args:
        bng_ref (BNGReference): A :class:`~osbng.bng_reference.BNGReference` object.
        d (int or float): The absolute distance d in metres.

    Returns:
        list[BNGReference]: All grid squares which have any part of their geometry
        within distance ``d`` of ``bng_ref``'s geometry

    Examples:
        >>> bng_dwithin(BNGReference("SU1234"), 1000)
        [
        BNGReference(bng_ref_formatted=SU 11 33, resolution_label=1km),
        BNGReference(bng_ref_formatted=SU 12 33, resolution_label=1km),
        BNGReference(bng_ref_formatted=SU 13 33, resolution_label=1km),
        BNGReference(bng_ref_formatted=SU 11 34, resolution_label=1km),
        BNGReference(bng_ref_formatted=SU 12 34, resolution_label=1km),
        BNGReference(bng_ref_formatted=SU 13 34, resolution_label=1km),
        BNGReference(bng_ref_formatted=SU 11 35, resolution_label=1km),
        BNGReference(bng_ref_formatted=SU 12 35, resolution_label=1km),
        BNGReference(bng_ref_formatted=SU 13 35, resolution_label=1km)
        ]
        >>> bng_dwithin(BNGReference("SU1234"), 1001)
        [list of 21 BNGReference objects]

    See Also:
        - The equivalent :meth:`osbng.bng_reference.BNGReference.bng_dwithin` instance
          method.
        - The :func:`~osbng.traversal.bng_distance` function and
          :meth:`osbng.bng_reference.BNGReference.bng_distance` instance method for
          calculating the distance between two input
          :class:`~osbng.bng_reference.BNGReference` objects.
    """
    # Convert distance to units of k
    k = int(np.ceil(d / bng_ref.resolution_metres))

    # Get full kdisc
    disc_refs = bng_kdisc(bng_ref, k)

    # Return only those whose centroids are within distance
    return [r for r in disc_refs if bng_distance(bng_ref, r, edge_to_edge=True) <= d]
