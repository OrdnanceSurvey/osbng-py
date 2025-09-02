"""Navigate the hierarchical structure of the BNG index system.

The British National Grid (BNG) is structured using a hierarchical system of grid
squares at various resolutions. At its highest level, the grid divides GB into 100 km by
100 km squares, each identified by a two-letter code. Successive levels of resolution
further subdivide the grid squares into finer detail, down to individual 1-meter
squares. This module allows for the traversal of this hierarchy by providing methods to
return the parent and children of :class:`~osbng.bng_reference.BNGReference` objects at
specified resolutions.

Parent and child definitions:
    - **Parent**: The parent of a :class:`~osbng.bng_reference.BNGReference` object is
      the grid square at the next higher (coarser) resolution level that contains the
      current reference. For example, the parent of a 1km grid square reference would be
      the 5km grid square that contains it.
    - **Children**: The children of a :class:`~osbng.bng_reference.BNGReference` object
      are the grid squares at the next lower (finer) resolution level that are contained
      within the current reference. For example, the children of a 10km grid square
      reference would be the 5km grid squares that it contains.

Notes:
    While parent and child derivation defaults to the next higher and lower
    resolution, any supported resolution in the hierarchy can be specified.

Supported Resolutions:
    - The module supports the 'standard' and 'intermediate' quadtree resolutions,
      including ``100km``, ``50km``, ``10km``, ``5km``, ``1km``, ``500m``, ``100m``,
      ``50m``, ``10m``, ``5m`` and ``1m``.
    - These resolutions passed to hierarchy functions are validated and normalised
      using the resolution mapping defined in the :doc:`resolution` module.
"""

from osbng.bng_reference import BNGReference, _validate_bngreferences
from osbng.errors import BNGHierarchyError
from osbng.indexing import (
    _validate_and_normalise_bng_resolution,
    bbox_to_bng,
    bng_to_xy,
    xy_to_bng,
)
from osbng.resolution import BNG_RESOLUTIONS

__all__ = ["bng_to_children", "bng_to_parent"]


@_validate_bngreferences
def bng_to_children(
    bng_ref: BNGReference, *, resolution: int | str | None = None
) -> list[BNGReference]:
    """Returns a list of child ``BNGReference`` objects of a ``BNGReference``.

    By default, the children of the :class:`~osbng.bng_reference.BNGReference` object is
    defined as the :class:`~osbng.bng_reference.BNGReference` objects in the next
    resolution down from the input :class:`~osbng.bng_reference.BNGReference` resolution
    . For example, 100km -> 50km.

    Notes:
        Any valid resolution can be provided as the child resolution, provided it is
        less than the resolution of the input :class:`~osbng.bng_reference.BNGReference`
        .

    Args:
        bng_ref (BNGReference): The :class:`~osbng.bng_reference.BNGReference` object to
            derive children from.

    Keyword Args:
        resolution (int | str | None, optional): The resolution of
            the children :class:`~osbng.bng_reference.BNGReference` objects expressed
            either as a metre-based integer or as a string label. Defaults to None.

    Returns:
        list[BNGReference]: A list of :class:`~osbng.bng_reference.BNGReference` objects
        that are children of the input :class:`~osbng.bng_reference.BNGReference` object
        .

    Raises:
        BNGReferenceError: If the first positional argument is not a
            :class:`~osbng.bng_reference.BNGReference` object.
        BNGHierarchyError: If the resolution of the input
            :class:`~osbng.bng_reference.BNGReference` object is 1m.
        BNGHierarchyError: If the resolution is greater than or equal to the resolution
            of the input :class:`~osbng.bng_reference.BNGReference` object.
        BNGResolutionError: If an invalid resolution is provided.

    Examples:
        >>> bng_to_children(BNGReference("SU"))
        [BNGReference(bng_ref_formatted=SU SW, resolution_label=50km),
        BNGReference(bng_ref_formatted=SU SE, resolution_label=50km),
        BNGReference(bng_ref_formatted=SU NW, resolution_label=50km),
        BNGReference(bng_ref_formatted=SU NE, resolution_label=50km)]
        >>> bng_to_children(BNGReference("SU36"))
        [BNGReference(bng_ref_formatted=SU 3 6 SW, resolution_label=5km),
        BNGReference(bng_ref_formatted=SU 3 6 SE, resolution_label=5km),
        BNGReference(bng_ref_formatted=SU 3 6 NW, resolution_label=5km),
        BNGReference(bng_ref_formatted=SU 3 6 NE, resolution_label=5km)]

    See Also:
        - The equivalent :meth:`osbng.bng_reference.BNGReference.bng_to_children`
          instance method.
        - :class:`~osbng.hierarchy.bng_to_parent` to derive the
          :class:`~osbng.bng_reference.BNGReference` object in the next resolution up.

    """
    # Raise error if the resolution is 1m
    if bng_ref.resolution_metres == 1:
        raise BNGHierarchyError("Cannot derive children from the finest 1m resolution")

    # Generate a scaled resolution if none is provided
    if resolution is None:
        resolution = bng_ref.resolution_metres

        if BNG_RESOLUTIONS[resolution]["quadtree"]:
            resolution = int((bng_ref.resolution_metres / 5))
        else:
            resolution = int((bng_ref.resolution_metres / 2))

    # Validate and normalise the resolution to its metre-based integer value
    validated_resolution = _validate_and_normalise_bng_resolution(resolution)

    # Raise error if the validated resolution is greater than the resolution of the
    # input BNGReference object
    if validated_resolution >= bng_ref.resolution_metres:
        raise BNGHierarchyError(
            "Resolution must be less than the resolution of input BNGReference object"
        )

    # Get min and max coordinates of the grid square bounding box
    min_coords = bng_to_xy(bng_ref, position="lower-left")
    max_coords = bng_to_xy(bng_ref, position="upper-right")

    # Derive children BNGReference objects from the bounding box
    bng_refs = bbox_to_bng(
        min_coords[0], min_coords[1], max_coords[0], max_coords[1], validated_resolution
    )

    return bng_refs


@_validate_bngreferences
def bng_to_parent(
    bng_ref: BNGReference, *, resolution: int | str | None = None
) -> BNGReference:
    """Returns the `BNGReference`that is the parent of a ``BNGReference``.

    By default, the parent of the :class:`~osbng.bng_reference.BNGReference` object is
    defined as the :class:`~osbng.bng_reference.BNGReference` in the next BNG resolution
    up from the input :class:`~osbng.bng_reference.BNGReference` resolution. For example
    , 50km -> 100km.

    Notes:
        Any valid resolution can be provided as the parent resolution, provided it is
        greater than the resolution of the input
        :class:`~osbng.bng_reference.BNGReference`.

    Args:
        bng_ref (BNGReference): The :class:`~osbng.bng_reference.BNGReference` object to
            derive parent from.

    Keyword Args:
        resolution (int | str | None, optional): The resolution of the parent
            :class:`~osbng.bng_reference.BNGReference` objects expressed either as a
            metre-based integer or as a string label. Defaults to None.

    Returns:
        BNGReference: A :class:`~osbng.bng_reference.BNGReference` object that is the
        parent of the input :class:`~osbng.bng_reference.BNGReference` object.

    Raises:
        BNGReferenceError: If the first positional argument is not a
            :class:`~osbng.bng_reference.BNGReference` object.
        BNGHierarchyError: If the resolution of the input
            :class:`~osbng.bng_reference.BNGReference` object is 100km.
        BNGHierarchyError: If the resolution is less than or equal to the resolution of
            the input :class:`~osbng.bng_reference.BNGReference` object.
        BNGResolutionError: If an invalid resolution is provided.

    Examples:
        >>> bng_to_parent(BNGReference("SU 3 6 SW"))
        BNGReference(bng_ref_formatted=SU 3 6, resolution_label=10km)
        >>> bng_to_parent(BNGReference("SU 342 567"))
        BNGReference(bng_ref_formatted=SU 34 56 NW, resolution_label=500m)
        >>> bng_to_parent(BNGReference("SU 342 567"), resolution=10000)
        BNGReference(bng_ref_formatted=SU 3 5, resolution_label=10km)

    See Also:
        - The equivalent :meth:`osbng.bng_reference.BNGReference.bng_to_parent`
          instance method.
        - :class:`~osbng.hierarchy.bng_to_children` to derive the
          :class:`~osbng.bng_reference.BNGReference` objects in the next resolution
          down.

    """
    # Raise error if the resolution is 100km
    if bng_ref.resolution_metres == 100000:
        raise BNGHierarchyError(
            "Cannot derive parent from the coarsest 100km resolution"
        )

    # Generate a scaled resolution if none is provided
    if resolution is None:
        resolution = bng_ref.resolution_metres

        if BNG_RESOLUTIONS[resolution]["quadtree"]:
            resolution = int((bng_ref.resolution_metres * 2))
        else:
            resolution = int((bng_ref.resolution_metres * 5))

    # Validate and normalise the resolution to its metre-based integer value
    validated_resolution = _validate_and_normalise_bng_resolution(resolution)

    # Raise error if the validated resolution is less than the resolution of the input
    # BNGReference object
    if validated_resolution <= bng_ref.resolution_metres:
        raise BNGHierarchyError(
            "Resolution must be greater than the resolution of input BNGReference "
            "object"
        )

    # Dervive coordinates of the grid square bounding box
    x, y = bng_to_xy(bng_ref, position="lower-left")

    # Derive parent BNGReference object from coordinates
    bng_ref = xy_to_bng(x, y, validated_resolution)

    return bng_ref
