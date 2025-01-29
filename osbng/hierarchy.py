"""Provides functionality for getting hierarchy BNG References.

This module supports hierachy functions to traverse the British National Grid.


Supported Resolutions:
    - The module supports the standard BNG resolutions, including 100km, 50km, 10km, 5km, 1km, 500m, 100m, 50m, 10m, 
    5m and 1m.
    - These resolutions are validated and normalised using the resolution mapping defined in the 'resolution' module.
"""

from osbng.indexing import xy_to_bng, bng_to_xy, bbox_to_bng
from osbng.bng_reference import BNGReference, _validate_bngreference
from osbng.indexing import _validate_and_normalise_bng_resolution
from osbng.resolution import _RESOLUTION_TO_STRING
from osbng.errors import BNGHierarchyError

__all__ = ["bng_to_children", "bng_to_parent"]


@_validate_bngreference
def bng_to_children(bng_ref: BNGReference, resolution=None) -> list[BNGReference]:
    """Returns a list of BNGReference objects that are children of the input BNGReference object.

    By default, the children of the BNGReference object is defined as the BNGReference objects in the
    next resolution down from the input BNGReference resolution. For example, 100km -> 50km.

    Any valid resolution can be provided as the child resolution, provided it is less than the
    resolution of the input BNGReference.

    Args:
        bng_ref (BNGReference): The BNGReference object to derive children from.
        resolution (int, optional): The resolution of the children BNGReference objects. Defaults to None.

    Returns:
        list[BNGReference]: A list of BNGReference objects that are children of the input BNGReference object.

    Raises:
        BNGHierarchyError: If the resolotuion of the input BNGReference object is 1m.
        BNGHIerarchyError: If the resolution is greater than or equal to the resolution of the input BNGReference object.
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
    """

    # Raise error if the resolution is 1m
    if bng_ref.resolution_metres == 1:
        raise BNGHierarchyError("Cannot derive children from the finest 1m resolution")

    # Generate a scaled resolution if none is provided
    if resolution is None:
        resolution = bng_ref.resolution_metres

        if _RESOLUTION_TO_STRING[resolution]["quadtree"]:
            resolution = int((bng_ref.resolution_metres / 5))
        else:
            resolution = int((bng_ref.resolution_metres / 2))

    # Validate and normalise the resolution to its metre-based integer value
    validated_resolution = _validate_and_normalise_bng_resolution(resolution)

    # Raise error if the validated resolution is greater than the resolution of the input BNGReference object
    if validated_resolution >= bng_ref.resolution_metres:
        raise BNGHierarchyError(
            "Resolution must be less than the resolution of input BNGReference object"
        )

    # Get min and max coordinates of the grid square bounding box
    min_coords = bng_to_xy(bng_ref, "lower-left")
    max_coords = bng_to_xy(bng_ref, "upper-right")

    # Derive children BNGReference objects from the bounding box
    bng_refs = bbox_to_bng(
        min_coords[0], min_coords[1], max_coords[0], max_coords[1], validated_resolution
    )

    return bng_refs


@_validate_bngreference
def bng_to_parent(bng_ref: BNGReference, resolution=None) -> BNGReference:
    """Returns a BNGReference object that is the parent of the input BNGReference object.

    By default, the parent of the BNGReference object is defined as the BNGReference in the next BNG
    resolution up from the input BNGReference resolution. For example, 50km -> 100km.

    Any valid resolution can be provided as the parent resolution, provided it is greater than the
    resolution of the input BNGReference.

    Args:
        bng_ref (BNGReference): The BNGReference object to derive parent from.
        resolution (int, optional): The resolution of the parent BNGReference. Defaults to None.

    Returns:
        BNGReference: A BNGReference object that is the parent of the input BNGReference object.

    Raises:
        BNGHierarchyError: If the resolution of the input BNGReference object is 100km.
        BNGHierarchyError: If the resolution is less than or equal to the resolution of the input BNGReference object.
        BNGResolutionError: If an invalid resolution is provided.

    Examples:
        >>> bng_to_parent(BNGReference("SU 3 6 SW"))
        BNGReference(bng_ref_formatted=SU 3 6, resolution_label=10km)
        >>> bng_to_parent(BNGReference("SU 342 567"))
        BNGReference(bng_ref_formatted=SU 34 56 NW, resolution_label=500m)
        >>> bng_to_parent(BNGReference("SU 342 567"), resolution=10000)
        BNGReference(bng_ref_formatted=SU 3 5, resolution_label=10km)

    """

    # Raise error if the resolution is 100km
    if bng_ref.resolution_metres == 100000:
        raise BNGHierarchyError(
            "Cannot derive parent from the coarsest 100km resolution"
        )

    # Generate a scaled resolution if none is provided
    if resolution is None:
        resolution = bng_ref.resolution_metres

        if _RESOLUTION_TO_STRING[resolution]["quadtree"]:
            resolution = int((bng_ref.resolution_metres * 2))
        else:
            resolution = int((bng_ref.resolution_metres * 5))

    # Validate and normalise the resolution to its metre-based integer value
    validated_resolution = _validate_and_normalise_bng_resolution(resolution)

    # Raise error if the validated resolution is less than the resolution of the input BNGReference object
    if validated_resolution <= bng_ref.resolution_metres:
        raise BNGHierarchyError(
            "Resolution must be greater than the resolution of input BNGReference object"
        )

    # Dervive coordinates of the grid square bounding box
    x, y = bng_to_xy(bng_ref, "lower-left")

    # Derive parent BNGReference object from coordinates
    bng_ref = xy_to_bng(x, y, validated_resolution)

    return bng_ref
