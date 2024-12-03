"""Provides functionality for indexing coordinates and geometries against the British National Grid (BNG).

The module supports bi-drectional conversion between easting/northing coordinate pairs and BNG references 
at supported resolutions as defined in the 'resolution' module. Additionally, it enables the decomposition 
of geometries, represented using Shapely objects,into simplified representations bounded by their presence 
in each grid square at a specified resolution. Indexing functionality faciliates grid-based spatial analysis, 
enabling applications such as statistical aggregation, data visualisation, and data interopability. 

Coordinate Conversion:
    - Convert eastng and northing coorindates to BNG references at supported resolutions.
    - Decode BNG references to retrieve the corresponding easting and northing coordinates.

Geometry Indexing: 
    - Retrieve the BNG references of the grid squares intersected by Shapely geometries at a specified resolution.
    - Decompose Shapely geometries of any type into the BNG grid squares they intersect at a specified resolution.

Supported Resolutions:
    - The module supports the standard BNG resolutions, inlcuding 100km, 50km, 10km, 5km, 1km, 500m, 100m, 50m, 10m, 
    5m and 1m.
    - These resolutions are validated and normalised usingthe resolution mapping defined in the 'resolution' module.
"""

import numpy as np

from osbng.errors import BNGResolutionError, OutsideBNGExtentError
from osbng.resolution import _RESOLUTION_TO_STRING
from osbng.bng_reference import BNGReference

# 100km BNG grid square letters
_PREFIXES = np.array(
    [
        ["SV", "SW", "SX", "SY", "SZ", "TV", "TW"],
        ["SQ", "SR", "SS", "ST", "SU", "TQ", "TR"],
        ["SL", "SM", "SN", "SO", "SP", "TL", "TM"],
        ["SF", "SG", "SH", "SJ", "SK", "TF", "TG"],
        ["SA", "SB", "SC", "SD", "SE", "TA", "TB"],
        ["NV", "NW", "NX", "NY", "NZ", "OV", "OW"],
        ["NQ", "NR", "NS", "NT", "NU", "OQ", "OR"],
        ["NL", "NM", "NN", "NO", "NP", "OL", "OM"],
        ["NF", "NG", "NH", "NJ", "NK", "OF", "OG"],
        ["NA", "NB", "NC", "ND", "NE", "OA", "OB"],
        ["HV", "HW", "HX", "HY", "HZ", "JV", "JW"],
        ["HQ", "HR", "HS", "HT", "HU", "JQ", "JR"],
        ["HL", "HM", "HN", "HO", "HP", "JL", "JM"],
    ]
)

# BNG ordinal direction suffixes and corresponding positional indices
# for intermediate quadtree resolutions
_SUFFIXES = {(0, 0): "SW", (0, 1): "NW", (1, 0): "SE", (1, 1): "NE"}


def _validate_and_normalise_bng_resolution(resolution: int | str):
    """Validates and normalises a BNG resolution to its metre-based integer value.

    Args:
        resolution (int or str): The Resolution, either as a metre-based integer or string label.

    Returns:
        int: The numeric metre-based resolution.

    Raises:
        BNGResolutionError: If an invalid resolution is provided.

    Example:
        >>> _validate_and_normalise_bng_resolution(1000)
        1000
        >>> _validate_and_normalise_bng_resolution("1km")
        1000
    """

    # If resolution is an integer, check if it's a valid metre-based resolution
    if isinstance(resolution, int):
        if resolution not in _RESOLUTION_TO_STRING.keys():
            raise BNGResolutionError()
        return resolution

    # If resolution is a string, check if it's a valid resolution label

    elif isinstance(resolution, str):
        if resolution not in [
            value["label"] for value in _RESOLUTION_TO_STRING.values()
        ]:
            raise BNGResolutionError()
        # Get the corresponding metre-based resolution
        return next(
            res
            for res, value in _RESOLUTION_TO_STRING.items()
            if value["label"] == resolution
        )

    # If resolution is neither an integer nor a string, raise BNGResolutionError
    else:
        raise BNGResolutionError()


def _validate_easting_northing(easting: float, northing: float):
    """Validates that the easting and northing coordinates are within the BNG extent.

    The easting and northing coordinates must be below the upper bounds of the BNG system.
    Coordinates of 700000 (easting) and 1300000 (northing) would correspond to a BNG reference
    representing the southwest (lower-left) corner of a grid square beyond the system's limits.

    Args:
        easting (float): The easting coordinate. Must be in the range 0 <= easting < 700000.
        northing (float): The northing coordinate. Must be in the range 0 <= northing < 1300000.

    Raises:
        OutsideBNGExtentError: If the easting or northing coordinates are outside the BNG extent.
    """
    if not (0 <= easting < 700000):
        raise OutsideBNGExtentError()
    if not (0 <= northing < 1300000):
        raise OutsideBNGExtentError()


def _get_bng_suffix(easting: float, northing: float, resolution: int) -> str:
    """Get the BNG ordinal direction suffix for a given easting, northing and quadtree resolution.

    Args:
        easting (float): Easting coordinate.
        northing (float): Northing coordinate.
        resolution (int): Resolution expressed as a metre-based integer. Must be an intermediate quadtree resolution e.g. 5, 50, 500, 5000, 50000.

    Returns:
        str: The BNG ordinal direction suffix.

    Example:
        >>> _get_bng_suffix(437289, 115541, 5000)
        'NE'
    """
    # Normalise easting and northing coordinates
    # Calculate the fractional part of the normalised easting and northing coordinates
    # Round fractional part to the nearest integer (0 or 1)
    suffix_x = round((easting % 100000) / (resolution * 2) % 1)
    suffix_y = round((northing % 100000) / (resolution * 2) % 1)

    # Return the suffix from the lookup using quadtree positional index
    return _SUFFIXES[suffix_x, suffix_y]


def xy_to_bng(easting: float, northing: float, resolution: int | str) -> BNGReference:
    """Returns a BNG reference object given easting and northing coordinates, at a specified resolution.

    Args:
        easting (float): The easting coordinate.
        northing (float): The northing coordinate.
        resolution (int or str): The resolution of the BNG reference expressed either as a metre-based integer or as a string label.

    Returns:
        BNGReference: The BNG reference object.

    Raises:
        BNGResolutionError: If an invalid resolution is provided.
        OutsideBNGExtentError: If the easting and northing coordinates are outside the BNG extent.

    Example:
        >>> xy_to_bng(437289, 115541, "100km").bng_ref_formatted
        'SU'
        >>> xy_to_bng(437289, 115541, "10km").bng_ref_formatted
        'SU 3 1'
        >>> xy_to_bng(437289, 115541, "5km").bng_ref_formatted
        'SU 3 1 NE'
        >>> xy_to_bng(437289, 115541, 1).bng_ref_formatted
        'SU 37289 15541'
    """
    # Validate and normalise the resolution to its metre-based integer value
    validated_resolution = _validate_and_normalise_bng_resolution(resolution)
    # Validate the easting and northing coordinates are within the BNG extent
    _validate_easting_northing(easting, northing)

    # Calculate prefix positional indices
    prefix_x = int(easting // 100000)
    prefix_y = int(northing // 100000)

    # Get the grid letters from the _PREFIX object
    prefix = _PREFIXES[prefix_y][prefix_x]

    # BNG reference for 100km resolution represents prefix only
    if validated_resolution == 100000:
        return BNGReference(prefix)

    # BNG reference for 50km resolution represents prefix and suffix
    elif validated_resolution == 50000:
        # Get BNG suffix
        suffix = _get_bng_suffix(easting, northing, validated_resolution)
        return BNGReference(f"{prefix}{suffix}")

    # All other BNG resolutions
    else:
        # Calculate scaled resolution for quadtree resolutions
        if _RESOLUTION_TO_STRING[validated_resolution]["quadtree"]:
            scaled_resolution = validated_resolution * 2
        else:
            scaled_resolution = validated_resolution

        # Calculate easting and northing bins
        easting_bin = int(easting % 100000 // scaled_resolution)
        northing_bin = int(northing % 100000 // scaled_resolution)

        # Padding length for variable easting and northing bin length
        pad_length = 6 - len(str(scaled_resolution))

        # Pad easting and northing bins
        easting_bin = str(easting_bin).zfill(pad_length)
        northing_bin = str(northing_bin).zfill(pad_length)

        # BNG reference for non-quadtree resolutions represents prefix, easting bin and northing bin
        if not _RESOLUTION_TO_STRING[validated_resolution]["quadtree"]:
            return BNGReference(f"{prefix}{easting_bin}{northing_bin}")
        # BNG reference for quadtree resolutions represents prefix, easting bin, northing bin and suffix
        else:
            # Get BNG suffix
            suffix = _get_bng_suffix(easting, northing, validated_resolution)
            return BNGReference(f"{prefix}{easting_bin}{northing_bin}{suffix}")
