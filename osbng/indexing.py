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
    - The module supports the standard BNG resolutions, including 100km, 50km, 10km, 5km, 1km, 500m, 100m, 50m, 10m, 
    5m and 1m.
    - These resolutions are validated and normalised using the resolution mapping defined in the 'resolution' module.
"""

import numpy as np

from osbng.errors import BNGResolutionError, OutsideBNGExtentError
from osbng.resolution import _RESOLUTION_TO_STRING
from osbng.bng_reference import _PATTERN, BNGReference, _validate_bngreference

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
_SUFFIXES = np.array([["SW", "NW"], ["SE", "NE"]])


def _validate_and_normalise_bng_resolution(resolution: int | str):
    """Validates and normalises a BNG resolution to its metre-based integer value.

    Args:
        resolution (int | str): The Resolution, either as a metre-based integer or string label.

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
    suffix_x = 1 if ((easting % 100000) / (resolution * 2) % 1) >= 0.5 else 0
    suffix_y = 1 if ((northing % 100000) / (resolution * 2) % 1) >= 0.5 else 0

    # Return the suffix from the lookup using quadtree positional index
    return _SUFFIXES[suffix_x, suffix_y]


def xy_to_bng(easting: float, northing: float, resolution: int | str) -> BNGReference:
    """Returns a BNG reference object given easting and northing coordinates, at a specified resolution.

    Args:
        easting (float): The easting coordinate.
        northing (float): The northing coordinate.
        resolution (int | str): The resolution of the BNG reference expressed either as a metre-based integer or as a string label.

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

    # Return the prefix from the lookup using positional indices
    prefix = _PREFIXES[prefix_y][prefix_x]

    # Calculate scaled resolution for quadtree resolutions
    if _RESOLUTION_TO_STRING[validated_resolution]["quadtree"]:
        scaled_resolution = validated_resolution * 2
        # Get BNG ordinal suffix
        suffix = _get_bng_suffix(easting, northing, validated_resolution)
    else:
        # For non-quadtree (standard) resolutions, the scaled resolution is the same as the resolution
        scaled_resolution = validated_resolution
        # No suffix for non-quadtree resolutions
        suffix = ""

    # Calculate easting and northing bins
    easting_bin = int(easting % 100000 // scaled_resolution)
    northing_bin = int(northing % 100000 // scaled_resolution)

    # Padding length for variable easting and northing bin length
    pad_length = 6 - len(str(scaled_resolution))

    # Pad easting and northing bins
    easting_bin = str(easting_bin).zfill(pad_length)
    northing_bin = str(northing_bin).zfill(pad_length)

    # Construct BNG reference for all resolutions less than 50km
    if validated_resolution < 50000:
        return BNGReference(f"{prefix}{easting_bin}{northing_bin}{suffix}")
    # BNG reference for 50km resolution consists of both prefix and suffix
    elif validated_resolution == 50000:
        return BNGReference(f"{prefix}{suffix}")
    # BNG reference for 100km resolution consist of the prefix only
    elif validated_resolution == 100000:
        return BNGReference(prefix)


@_validate_bngreference
def bng_to_xy(
    bng_ref: BNGReference, position: str = "lower-left"
) -> tuple[int | float, int | float]:
    """Returns the easting and northing coordinates given a BNG reference object, at a specified grid cell position.

    Args:
        bng_ref (BNGReference): The BNG Reference object.
        position (str): The grid cell position expressed as a string.
                        One of: 'lower-left', 'upper-left', 'upper-right', 'lower-right', 'centre'.

    Returns:
        easting, northing (tuple[int | float, int | float]): The easting and northing coordinates as a tuple.

    Raises:
        ValueError: If invalid position provided.

    Example:
        >>> bng_to_xy(BNGReference("SU"), "lower-left")
        (400000, 100000)
        >>> bng_to_xy(BNGReference("SU 3 1"), "lower-left")
        (430000, 110000)
        >>> bng_to_xy(BNGReference("SU 3 1 NE"), "centre")
        (437500, 117500)
        >>> bng_to_xy(BNGReference("SU 37289 15541"), "centre)
        (437289.5, 115541.5)
    """
    # validate position string
    valid_positions = [
        "lower-left",
        "upper-left",
        "upper-right",
        "lower-right",
        "centre",
    ]

    if position not in valid_positions:
        raise ValueError(
            f"Invalid position provided. Supported positions are: {", ".join(p for p in valid_positions)}"
        )

    # Extract resolution in metres from BNG reference
    resolution = bng_ref.resolution_metres

    # Get the pattern match for the BNG reference in the compact format
    match = _PATTERN.match(bng_ref.bng_ref_compact)
    # Extract prefix, numerical component and suffix of the BNG reference
    prefix = match.group(1)
    en_components = match.group(2)
    suffix = match.group(3)

    # Get the prefix indices from prefix position in _PREFIXES array
    prefix_indices = np.argwhere(_PREFIXES == prefix)[0]

    # Convert the prefix indices to easting and northing coordinates of 100km grid square
    prefix_easting = int(prefix_indices[1] * 100000)
    prefix_northing = int(prefix_indices[0] * 100000)

    # For quadtree resolutions, scale the resolution value by 2
    if _RESOLUTION_TO_STRING[resolution]["quadtree"]:
        scaled_resolution = resolution * 2

    # For non-quadtree (standard) resolutions, the scaled resolution is the same as the resolution
    else:
        scaled_resolution = resolution

    # Generate the offset values from the en_components
    if en_components:
        length = len(en_components)
        easting_offset = int(en_components[: length // 2]) * scaled_resolution
        northing_offset = int(en_components[length // 2 :]) * scaled_resolution

    # For 100km grid square, no additional offset is required
    else:
        easting_offset = 0
        northing_offset = 0

    # Generate the suffix values from the position in the _SUFFIXES array
    if suffix:
        suffix_indices = np.argwhere(_SUFFIXES == suffix)[0]
        # Convert the suffix indices to coordinate values by multiplying by the resolution
        suffix_easting = int(suffix_indices[0] * resolution)
        suffix_northing = int(suffix_indices[1] * resolution)

    # For standard resolutions, no suffix easting or northing is required
    else:
        suffix_easting = 0
        suffix_northing = 0

    # Compile the easting and northing values of the lower-left corner of the grid cell
    easting = prefix_easting + easting_offset + suffix_easting
    northing = prefix_northing + northing_offset + suffix_northing

    # If position is lower-left, coordinates remain unchanged
    if position == "lower-left":
        return easting, northing
    # If position is upper-left, add resolution value to northing
    elif position == "upper-left":
        return easting, northing + resolution
    # If position is upper-right, add resolution value to easting and northing
    elif position == "upper-right":
        return easting + resolution, northing + resolution
    # If postion is lower-right, add resolution value to easting
    elif position == "lower-right":
        return easting + resolution, northing
    # If position is centre, add half the resolution value to easting and northing
    elif position == "centre":
        easting = easting + (resolution / 2)
        northing = northing + (resolution / 2)
        # Cast as integer type if fractional part is equal to .0
        if easting % 1 == 0:
            easting = int(easting)
        if northing % 1 == 0:
            northing = int(northing)
        return easting, northing