"""Provides functionality to index coordinates and Shapely geometries within the British National Grid (BNG) index system.

The module supports bi-directional conversion between easting/northing coordinate pairs and BNGReference objects
at supported resolutions as defined in the 'resolution' module. Additionally, it enables the indexing of geometries, 
represented using Shapely Geometry objects, into grid squares at a specified resolution. Shapely geometries can also be decomposed
into simplified representations bounded by their presence in each grid square at a specified resolution.

Indexing functionality faciliates grid-based spatial analysis, enabling applications such as statistical aggregation, 
data visualisation, and data interopability. 

Summary of functionality:

    - Encoding easting and northing coordinates into BNGReference objects at a specified resolution.
    - Decoding BNGReference objects back into easting/nothing coordinates, bounding boxes and grid squares as Shapely geometries.
    - Indexing bounding boxes into grid squares at a specified resolution.
    - Indexing Shapely geometries into grid squares at a specified resolution.
    - Decomposing Shapely geometries into simplified representations bounded by their presence in each grid square at 
      a specified resolution.

Supported resolutions:

    - The module supports the 'standard' and 'intermediate' quadtree resolutions: 100km, 50km, 10km, 5km, 1km, 500m, 100m, 
      50m, 10m, 5m and 1m.
    - These resolutions passed to indexing functions are validated and normalised using the resolution mapping defined in the 
      'resolution' module.
"""

import warnings

import numpy as np
from shapely import box, contains, Geometry, intersection, intersects, prepare
from shapely.geometry import Polygon

from osbng.bng_reference import _PATTERN, _validate_bngreference, BNGReference
from osbng.errors import BNGExtentError, BNGResolutionError
from osbng.resolution import BNG_RESOLUTIONS

__all__ = [
    "PREFIXES",
    "SUFFIXES",
    "BNGIndexedGeometry",
    "xy_to_bng",
    "bng_to_xy",
    "bng_to_bbox",
    "bng_to_grid_geom",
    "bbox_to_bng",
    "geom_to_bng",
    "geom_to_bng_intersection"
]

# Set warnings to always display
warnings.simplefilter("always")

# 100km BNG grid square letter prefixes and corresponding positional indices
PREFIXES = np.array(
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
# Used to identify intermediate quadtree resolutions
SUFFIXES = np.array([["SW", "NW"], ["SE", "NE"]])


class BNGIndexedGeometry:
    """Represents the decomposition of a Shapely Geometry object into BNG grid squares at a specified resolution.

    The BNGIndexedGeometry class stores information about the relationship between an input geometry and the grid squares
    it intersects. This is particularly useful for spatial indexing and analysis of geometries against the BNG system.

    Attributes:
        bng_ref (BNGReference): The BNGReference object representing the grid square corresponding to the decomposition.
        is_core (bool): A Boolean flag indicating whether the grid square geometry is entirely contained by the input
                        geometry. This is relevant for Polygon geometries and helps distinguish between "core" (fully inside)
                        and "edge" (partially overlapping) grid squares.
        geom (Geometry): The Shapely Geometry representing the intersection between the input geometry and the grid square.
                         This can one of a number of geometry types depending on the overlap. When is_core is True,
                         geom is the same as the grid square geometry.

    Usage:
        The BNGIndexedGeometry class is instantiated as part of the geom_to_bng_intersection indexing function that decomposes a
        Shapely Geometry into grid squares at a specified resolution. The decomposition can be used for indexing, spatial analysis,
        or visualisation."""

    def __init__(self, bng_ref: BNGReference, is_core: bool, geom: Geometry):
        """Initialises a BNGIndexedGeometry object instance."""
        self._bng_ref = bng_ref
        self._is_core = is_core
        self._geom = geom

    @property
    def bng_ref(self):
        """Returns the BNGReference object associated with this geometry."""
        return self._bng_ref

    @property
    def is_core(self):
        """Indicates whether the grid square geometry is contained by the input geometry."""
        return self._is_core

    @property
    def geom(self):
        """Returns the Shapely Geometry representing the intersection between the input geometry and the grid square."""
        return self._geom

    def __repr__(self):
        return (
            f"BNGIndexedGeometry(bng_ref={self._bng_ref}, "
            f"is_core={self._is_core}, geom={self._geom.wkt})"
        )


def _validate_and_normalise_bng_resolution(resolution: int | str) -> int:
    """Validates and normalises a BNG resolution to its metre-based integer value.

    Args:
        resolution (int | str): The resolution, either as a metre-based integer or string label.

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
        if resolution not in BNG_RESOLUTIONS.keys():
            raise BNGResolutionError()
        return resolution

    # If resolution is a string, check if it's a valid resolution label
    elif isinstance(resolution, str):
        if resolution not in [value["label"] for value in BNG_RESOLUTIONS.values()]:
            raise BNGResolutionError()
        # Get the corresponding metre-based resolution
        return next(
            res
            for res, value in BNG_RESOLUTIONS.items()
            if value["label"] == resolution
        )

    # If resolution is neither an integer nor a string, raise BNGResolutionError
    else:
        raise BNGResolutionError()


def _validate_easting_northing(easting: int | float, northing: int | float):
    """Validates that easting and northing coordinates are within the bounds of the BNG index system extent.

    The easting and northing coordinates must be below the upper bounds of the BNG system.
    Coordinates of 700000 (easting) and 1300000 (northing) would correspond to a BNG reference
    representing the southwest (lower-left) corner of a grid square beyond the system's limits.

    Args:
        easting (int | float): The easting coordinate. Must be in the range 0 <= easting < 700000.
        northing (int | float): The northing coordinate. Must be in the range 0 <= northing < 1300000.

    Raises:
        BNGExtentError: If the easting or northing coordinates are outside the BNG extent.
    """
    if not (0 <= easting < 700000):
        raise BNGExtentError()
    if not (0 <= northing < 1300000):
        raise BNGExtentError()


def _validate_and_normalise_bbox(
    xmin: int | float, ymin: int | float, xmax: int | float, ymax: int | float
) -> tuple[int | float, int | float, int | float, int | float]:
    """Validates and normalises bounding box coordinates to the BNG index system extent.

    Args:
        xmin (int | float): The minimum easting coordinate of the bounding box.
        ymin (int | float): The minimum northing coordinate of the bounding box.
        xmax (int | float): The maximum easting coordinate of the bounding box.
        ymax (int | float): The maximum northing coordinate of the bounding box.

    Returns:
        tuple[float, float, float, float]: The normalised bounding box coordinates.
    """
    # Initialise list to store warning messages
    messages = []

    # Normalise xmin and ymin to 0 if xmin < 0 or ymin < 0
    if xmin < 0:
        messages.append(f"xmin < 0, normalising {xmin} to 0")
        xmin = 0
    if ymin < 0:
        messages.append(f"ymin < 0, normalising {ymin} to 0")
        ymin = 0

    # Normalise xmax to 700000 if xmax > 700000
    if xmax > 700000:
        messages.append(f"xmax > 700000, normalising {xmax} to 700000")
        xmax = 700000

    # Normalise ymax to 1300000 if ymax > 1300000
    if ymax > 1300000:
        messages.append(f"ymax > 1300000, normalising {ymax} to 1300000")
        ymax = 1300000

    if messages:
        warnings.warn(
            "Bounding box coordinates fall outside of the BNG index system extent: \n"
            + "\n".join(messages)
        )

    return xmin, ymin, xmax, ymax


def _get_bng_suffix(easting: int | float, northing: int | float, resolution: int) -> str:
    """Get the BNG ordinal direction suffix for a given easting, northing and quadtree resolution.

    Args:
        easting (int | float): Easting coordinate.
        northing (int | float): Northing coordinate.
        resolution (int): Resolution expressed as a metre-based integer. Must be an intermediate quadtree
                          resolution e.g. 5, 50, 500, 5000, 50000.

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
    return SUFFIXES[suffix_x, suffix_y]


def _decompose_geom(geom: Geometry) -> list[Geometry]:
    """Recursively decompose a Shapely Geometry into its constituent parts.

    Args:
        geom (Geometry): Shapely Geometry object.

    Returns:
        list[Geometry]: List of Shapely Geometry object parts.

    Raises:
        ValueError: If the geometry type is not supported.
    """
    # Single part geometries are returned as-is
    if geom.geom_type in ["Point", "LineString", "Polygon"]:
        return [geom]

    # Multi-part geometries are decomposed into their constituent parts
    elif geom.geom_type in [
        "MultiPoint",
        "MultiLineString",
        "MultiPolygon",
        "GeometryCollection",
    ]:
        # Initialise list to store decomposed geometries
        geometries = []
        # Recursively decompose each part of the multi-part geometry
        for part in geom.geoms:
            geometries.extend(_decompose_geom(part))
        return geometries

    # Raise an error if the geometry type is not supported
    else:
        raise ValueError(f"Unsupported geometry type: {geom.geom_type}")


def xy_to_bng(easting: int | float, northing: int | float, resolution: int | str) -> BNGReference:
    """Returns a BNGReference object given easting and northing coordinates, at a specified resolution.

    Args:
        easting (int | float): The easting coordinate.
        northing (int | float): The northing coordinate.
        resolution (int | str): The resolution of the BNG reference expressed either as a metre-based integer or as a string label.

    Returns:
        BNGReference: The BNGReference object.

    Raises:
        BNGResolutionError: If an invalid resolution is provided.
        BNGExtentError: If the easting and northing coordinates are outside the BNG extent.

    Example:
        >>> xy_to_bng(437289, 115541, "100km")
        BNGReference(bng_ref_formatted=SU, resolution_label=100km)
        >>> xy_to_bng(437289, 115541, "10km")
        BNGReference(bng_ref_formatted=SU 3 1, resolution_label=10km)
        >>> xy_to_bng(437289, 115541, "5km")
        BNGReference(bng_ref_formatted=SU 3 1 NE, resolution_label=5km)
        >>> xy_to_bng(437289, 115541, 1)
        BNGReference(bng_ref_formatted=SU 37289 15541, resolution_label=1m)
    """
    # Validate and normalise the resolution to its metre-based integer value
    validated_resolution = _validate_and_normalise_bng_resolution(resolution)
    # Validate the easting and northing coordinates are within the BNG extent
    _validate_easting_northing(easting, northing)

    # Calculate prefix positional indices
    prefix_x = int(easting // 100000)
    prefix_y = int(northing // 100000)

    # Return the prefix from the lookup using positional indices
    prefix = PREFIXES[prefix_y][prefix_x]

    # Calculate scaled resolution for quadtree resolutions
    if BNG_RESOLUTIONS[validated_resolution]["quadtree"]:
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
        bng_ref (BNGReference): The BNG eference object.
        position (str): The grid cell position expressed as a string.
                        One of: 'lower-left', 'upper-left', 'upper-right', 'lower-right', 'centre'.

    Returns:
        tuple[int | float, int | float]: The easting and northing coordinates as a tuple.

    Raises:
        BNGReferenceError: If the first positional argument is not a BNGReference object.
        TypeError: If the first argumnet is not BNGReference object.
        ValueError: If an invalid position provided.

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
            f"Invalid position provided. Supported positions are: {', '.join(p for p in valid_positions)}"
        )

    # Extract resolution in metres from BNG reference
    resolution = bng_ref.resolution_metres

    # Get the pattern match for the BNG reference in the compact format
    match = _PATTERN.match(bng_ref.bng_ref_compact)
    # Extract prefix, numerical component and suffix of the BNG reference
    prefix = match.group(1)
    en_components = match.group(2)
    suffix = match.group(3)

    # Get the prefix indices from prefix position in PREFIXES array
    prefix_indices = np.argwhere(PREFIXES == prefix)[0]

    # Convert the prefix indices to easting and northing coordinates of 100km grid square
    prefix_easting = int(prefix_indices[1] * 100000)
    prefix_northing = int(prefix_indices[0] * 100000)

    # For quadtree resolutions, scale the resolution value by 2
    if BNG_RESOLUTIONS[resolution]["quadtree"]:
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

    # Generate the suffix values from the position in the SUFFIXES array
    if suffix:
        suffix_indices = np.argwhere(SUFFIXES == suffix)[0]
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


@_validate_bngreference
def bng_to_bbox(bng_ref: BNGReference) -> tuple[int, int, int, int]:
    """Returns grid square bounding box coordinates given a BNGReference object.

    Args:
        bng_ref (BNGReference): The BNGReference object.

    Returns:
        tuple[int, int, int, int]: The grid square bounding box coordinates (min x, min y, max x, max y) as a tuple.

    Raises:
        TypeError: If first argumnet is not BNGReference object.

    Example:
        >>> bng_to_bbox(BNGReference("SU"))
        (400000, 100000, 500000, 200000)
        >>> bng_to_bbox(BNGReference("SU 3 1"))
        (430000, 110000, 440000, 120000)
        >>> bng_to_bbox(BNGReference("SU 3 1 NE"))
        (435000, 115000, 440000, 120000)
        >>> bng_to_bbox(BNGReference("SU 37289 15541"))
        (437289, 115541, 437290, 115542)
    """
    # Extract lower left and upper right coordinates of grid square
    min_xy = bng_to_xy(bng_ref, "lower-left")
    max_xy = bng_to_xy(bng_ref, "upper-right")

    return min_xy + max_xy


@_validate_bngreference
def bng_to_grid_geom(bng_ref: BNGReference) -> Polygon:
    """Returns a grid square as a Shapely Polygon given a BNG Reference object.

    Args:
        bng_ref (BNGReference): The BNGReference object.

    Returns:
        Polygon: Grid square as Shapely Polygon object.

    Raises:
        BNGReferenceError: If the first positional argument is not a BNGReference object.
        TypeError: If first argument is not BNG Reference object.

    Example:
        >>> bng_to_grid_geom(BNGReference("SU")).wkt
        'POLYGON ((500000 100000, 500000 200000, 400000 200000, 400000 100000, 500000 100000))'
        >>> bng_to_grid_geom(BNGReference("SU 3 1")).wkt
        'POLYGON ((440000 110000, 440000 120000, 430000 120000, 430000 110000, 440000 110000))'
        >>> bng_to_grid_geom(BNGReference("SU 3 1 NE")).wkt
        'POLYGON ((440000 115000, 440000 120000, 435000 120000, 435000 115000, 440000 115000))'
        >>> bng_to_grid_geom(BNGReference("SU 37289 15541")).wkt
        'POLYGON ((437290 115541, 437290 115542, 437289 115542, 437289 115541, 437290 115541))'
    """
    return box(*bng_to_bbox(bng_ref))


def bbox_to_bng(
    xmin: int | float, ymin: int | float, xmax: int | float, ymax: int | float, resolution: int | str
) -> list[BNGReference]:
    """Returns a list of BNGReference objects given bounding box coordinates and a resolution.

    The relationship between the bounding box and the returned BNG grid squares depends on the
    alignment of the bounding box with the BNG index system:

    - **Aligned Bounding Box**: If the bounding box edges align with the BNG system
        (e.g. xmin, ymin, xmax, ymax are multiples of the specified resolution), only the grid
        squares entirely contained within the bounding box are returned. Grid squares that intersect
        but are not fully contained within the bounding box are excluded.

    - **Non-Aligned Bounding Box**: If the bounding box edges are not aligned with the BNG system,
        grid squares that are partially overlapped by the bounding box are also included. In this case,
        the function ensures all relevant grid squares that the bounding box touches are returned,
        including those at the edges.

    Validates and normalises the bounding box coordinates to the BNG index system extent. If bounding box
    coordinates fall outside of the BNG system extent, then a warning is raised and the coordinates are snapped
    to the bounds of the BNG system.

    Args:
        xmin (int | float): The minimum easting coordinate of the bounding box.
        ymin (int | float): The minimum northing coordinate of the bounding box.
        xmax (int | float): The maximum easting coordinate of the bounding box.
        ymax (int | float): The maximum northing coordinate of the bounding box.
        resolution (int | str): The resolution of the BNG reference expressed either as a metre-based integer or as a string label.

    Returns:
        list[BNGReference]: List of BNGReference objects.

    Raises:
        BNGResolutionError: If an invalid resolution is provided.

    Example:
        >>> bbox_to_bng(400000, 100000, 500000, 200000, "50km")
        [BNGReference(bng_ref_formatted=SU SW, resolution_label=50km), 
         BNGReference(bng_ref_formatted=SU SE, resolution_label=50km),
         BNGReference(bng_ref_formatted=SU NW, resolution_label=50km),
         BNGReference(bng_ref_formatted=SU NE, resolution_label=50km)]
        >>> bbox_to_bng(285137.06, 78633.75, 299851.01, 86427.96, 5000)
        [BNGReference(bng_ref_formatted=SX 8 7 NE, resolution_label=5km),
         BNGReference(bng_ref_formatted=SX 9 7 NW, resolution_label=5km),
         BNGReference(bng_ref_formatted=SX 9 7 NE, resolution_label=5km),
         BNGReference(bng_ref_formatted=SX 8 8 SE, resolution_label=5km),
         BNGReference(bng_ref_formatted=SX 9 8 SW, resolution_label=5km),
         BNGReference(bng_ref_formatted=SX 9 8 SE, resolution_label=5km),
         BNGReference(bng_ref_formatted=SX 8 8 NE, resolution_label=5km),
         BNGReference(bng_ref_formatted=SX 9 8 NW, resolution_label=5km),
         BNGReference(bng_ref_formatted=SX 9 8 NE, resolution_label=5km)] 
    """

    # Validate and normalise the resolution to its metre-based integer value
    validated_resolution = _validate_and_normalise_bng_resolution(resolution)

    # Validate and normalise bounding box coordinates to the BNG index system extent
    xmin, ymin, xmax, ymax = _validate_and_normalise_bbox(xmin, ymin, xmax, ymax)

    # Snap the maximum easting and maximum northing coordinates to an integer multiple of resolution
    xmax_snapped = int(np.ceil(xmax / validated_resolution) * validated_resolution)
    ymax_snapped = int(np.ceil(ymax / validated_resolution) * validated_resolution)

    # Generate a grid of easting and northing coordinates
    eastings = np.arange(xmin, xmax_snapped, validated_resolution)
    northings = np.arange(ymin, ymax_snapped, validated_resolution)

    # For vertical or horizontal lines which exactly align with the grid boundaries,
    # the above returns an empty list, so ensure that at least one element is in the eastings and northings
    eastings = eastings if len(eastings) > 0 else np.array([xmax_snapped])
    northings = northings if len(northings) > 0 else np.array([ymax_snapped])

    easting_grid, northing_grid = np.meshgrid(eastings, northings)

    # Flatten grids for iteration
    easting_grid = easting_grid.ravel()
    northing_grid = northing_grid.ravel()

    # Convert grid coordinates to BNGReference objects
    bng_refs = [
        xy_to_bng(easting, northing, validated_resolution)
        for easting, northing in zip(easting_grid, northing_grid)
    ]

    return bng_refs


def geom_to_bng(geom: Geometry, resolution: int | str) -> list[BNGReference]:
    """Returns a list of BNGReference objects given a Shapely Geometry and a specified resolution.

       The BNGReference objects returned represent the grid squares intersected by the input geometry.
       BNGReference objects are deduplicated in cases where two or more parts of a multi-part geometry
       intersect the same grid square.
       
       This function is useful for spatial indexing and aggregation of geometries against the BNG. 
       For geometry decomposition by the BNG index system, use geom_to_bng_intersection instead.

       A note on the type of the input geometry. This also applies to the parts within a multi-part geometry:

         - For Point geometries, the function returns a list comprising a single BNGReference object. A BNGExtentError
           exception is raised if the coordinates are outside of the BNG index system extent.
         - For LineString and Polygon geometry types, the function returns a list of BNGReference objects representing the
           grid squares intersected by the geometry. When the geometry extends beyond the BNG system extent, the function
           will show a feature bounding box warning but will still return the BNGReference objects for the intersected grid
           squares.

    Args:
        geom (Geometry): Shapely Geometry object.
        resolution (int | str): The BNG resolution expressed either as a metre-based integer or as a string label.

    Returns:
        list[BNGReference]: List of BNGReference objects.

    Raises:
        BNGResolutionError: If an invalid resolution is provided.
        ValueError: If the geometry type is not supported.
        BNGExtentError: If the coordinates of a point geometry are outside of the BNG index system extent.

    Example:
        >>> geom_to_bng(Point(430000, 110000), "100km")
        [BNGReference(bng_ref_formatted=SU, resolution_label=100km)]
        >>> geom_to_bng(LineString([[430000, 110000],[430010, 110000],[430010, 110010]]), "5m")
        [BNGReference(bng_ref_formatted=SU 3000 1000 SE, resolution_label=5m),
         BNGReference(bng_ref_formatted=SU 3000 1000 SW, resolution_label=5m),
         BNGReference(bng_ref_formatted=SU 3000 1000 NE, resolution_label=5m)]
    """
    # Validate and normalise the resolution to its metre-based integer value
    validated_resolution = _validate_and_normalise_bng_resolution(resolution)

    # Initialise an empty list to store the BNGReference objects
    bng_refs = []

    # Recursively decompose geometry into its constituent parts
    for part in _decompose_geom(geom):

        if part.geom_type == "Point":
            # Convert the Point to BNGReference object and append to bng_refs list
            bng_refs.append(xy_to_bng(part.x, part.y, validated_resolution))

        # All other geometry types
        else:
            # Get the bounding box of the geometry part
            bbox = part.bounds
            # Convert the bounding box to BNGReference objects
            _bng_refs = np.array(bbox_to_bng(*bbox, validated_resolution))
            # Get the grid square geometries of the BNGReference objects
            bng_geoms = np.array([bng_to_grid_geom(bng_ref) for bng_ref in _bng_refs])
            # Prepare the geometry part to speed up intersects spatial predicate tests
            prepare(part)
            # Test where the geometry part intersects the grid square geometries
            bng_bool = intersects(part, bng_geoms)
            # Append the intersected BNGReference objects to the bng_refs list
            bng_refs.extend(_bng_refs[bng_bool].tolist())

    # Deduplicate the list of BNGReference objects
    return list(set(bng_refs))


def geom_to_bng_intersection(
    geom: Geometry, resolution: int | str
) -> list[BNGIndexedGeometry]:
    """Returns a list of BNGIndexedGeometry objects given a Shapely Geometry and a specified resolution.

       Decomposes a Shapely Geometry into BNG grid squares at a specified resolution. Unlike geom_to_bng which only returns
       BNGReference objects representing the grid squares intersected by the input geometry, geom_to_bng_intersection returns
       BNGIndexedGeometry objects that store the intersection between the input geometry and the grid square geometries.

       This is particularly useful for spatial indexing, aggregation and visualisation use cases that requires the decomposition
       of geometries into their constituent parts bounded by the BNG system.

       A note on the type of the input geometry. This also applies to the parts within a multi-part geometry:

        - For Point geometries, the function returns a list comprising a single BNGIndexedGeometry object. A BNGExtentError
          exception is raised if the coordinates are outside of the BNG index system extent.
        - For LineString and Polygon geometry types, the function returns a list of BNGIndexedGeometry objects representing the
          intersections between the grid squares and the geometry. When the geometry extends beyond the BNG system extent, the function
          will show a feature bounding box warning but will still return the BNGIndexedGeometry objects for the intersected grid
          squares.

    Args:
        geom (Geometry): Shapely Geometry object.
        resolution (int | str): The BNG resolution expressed either as a metre-based integer or as a string label.

    Returns:
        list[BNGIndexedGeometry]: List of BNGIndexedGeometry objects.

    Raises:
        BNGResolutionError: If an invalid resolution is provided.
        ValueError: If the geometry type is not supported.
        BNGExtentError: If the coordinates of a point geometry are outside of the BNG index system extent.

    Example:
        >>> geom_to_bng_intersection(Point(430000, 110000), "100km")
        [BNGIndexedGeometry(bng_ref=BNGReference(bng_ref_formatted=SU, resolution_label=100km), is_core=False, geom=POINT (430000 110000))]
        >>> geom_to_bng_intersection(LineString([[430000, 110000],[430010, 110000],[430010, 110010]]), "5m")
        [BNGIndexedGeometry(bng_ref=BNGReference(bng_ref_formatted=SU 3000 1000 SE, resolution_label=5m), is_core=False, geom=MULTILINESTRING ((430005 110000, 430010 110000), (430010 110000, 430010 110005))),
         BNGIndexedGeometry(bng_ref=BNGReference(bng_ref_formatted=SU 3000 1000 SW, resolution_label=5m), is_core=False, geom=LINESTRING (430000 110000, 430005 110000)),
         BNGIndexedGeometry(bng_ref=BNGReference(bng_ref_formatted=SU 3000 1000 NE, resolution_label=5m), is_core=False, geom=LINESTRING (430010 110005, 430010 110010))]
        >>> from shapely import wkt
        >>> geom_to_bng_intersection(wkt.loads("Polygon ((375480.64511692 144999.23691181, 426949.67604058 160255.02751493, 465166.20199588 153320.57724078, 453762.88376729 94454.79935802, 393510.2158297 91989.21703833, 375480.64511692 144999.23691181))"), "50km")
        [BNGIndexedGeometry(bng_ref=BNGReference(bng_ref_formatted=SU SW, resolution_label=50km), is_core=True, geom=POLYGON ((450000 100000, 450000 150000, 400000 150000, 400000 100000, 450000 100000))),
         BNGIndexedGeometry(bng_ref=BNGReference(bng_ref_formatted=ST NE, resolution_label=50km), is_core=False, geom=POLYGON ((400000 152266.94988613573, 400000 150000, 392351.90644475375 150000, 400000 152266.94988613573))),
         BNGIndexedGeometry(bng_ref=BNGReference(bng_ref_formatted=ST SE, resolution_label=50km), is_core=False, geom=POLYGON ((392351.90644475375 150000, 400000 150000, 400000 100000, 390785.6181363417 100000, 375480.64511692 144999.23691181, 392351.90644475375 150000))),
         BNGIndexedGeometry(bng_ref=BNGReference(bng_ref_formatted=SZ NW, resolution_label=50km), is_core=False, geom=POLYGON ((400000 92254.78365399371, 400000 100000, 450000 100000, 450000 94300.8194596147, 400000 92254.78365399371))),
         BNGIndexedGeometry(bng_ref=BNGReference(bng_ref_formatted=SZ NE, resolution_label=50km), is_core=False, geom=POLYGON ((453762.88376729 94454.79935802, 450000 94300.8194596147, 450000 100000, 454837.0849387723 100000, 453762.88376729 94454.79935802))),
         BNGIndexedGeometry(bng_ref=BNGReference(bng_ref_formatted=SU SE, resolution_label=50km), is_core=False, geom=POLYGON ((454837.0849387723 100000, 450000 100000, 450000 150000, 464522.9488131115 150000, 454837.0849387723 100000))),
         BNGIndexedGeometry(bng_ref=BNGReference(bng_ref_formatted=SU NE, resolution_label=50km), is_core=False, geom=POLYGON ((465166.20199588 153320.57724078, 464522.9488131115 150000, 450000 150000, 450000 156072.50905454965, 465166.20199588 153320.57724078))),
         BNGIndexedGeometry(bng_ref=BNGReference(bng_ref_formatted=SU NW, resolution_label=50km), is_core=False, geom=POLYGON ((426949.67604058 160255.02751493, 450000 156072.50905454965, 450000 150000, 400000 150000, 400000 152266.94988613573, 426949.67604058 160255.02751493))),
         BNGIndexedGeometry(bng_ref=BNGReference(bng_ref_formatted=SY NE, resolution_label=50km), is_core=False, geom=POLYGON ((393510.2158297 91989.21703833, 390785.6181363417 100000, 400000 100000, 400000 92254.78365399371, 393510.2158297 91989.21703833)))]
    """
    # Initialise an empty list to store the BNGIndexedGeometry objects
    bng_idx_geoms = []

    # Recursively decompose geometry into its constituent parts
    for part in _decompose_geom(geom):
        
        # Convert the geometry part to BNGReference objects
        bng_refs = np.array(geom_to_bng(part, resolution))

        if part.geom_type == "Point":
            # Convert the Point to a BNGIndexedGeometry object and append to bng_idx_geoms list
            bng_idx_geoms.append(BNGIndexedGeometry(bng_refs[0], False, part))

        elif part.geom_type == "LineString":
            # Get the grid square geometries of the BNGReference objects
            bng_geoms = np.array([bng_to_grid_geom(bng_ref) for bng_ref in bng_refs])
            # Prepare the geometry part to speed up intersects spatial predicate tests
            prepare(part)
            # Derive the intersections between the geometry part and the grid square geometries
            intersections = intersection(part, bng_geoms)
            # Derive BNGIndexedGeometry objects for geometry part and add to the bng_idx_geoms list
            bng_idx_geoms.extend(
                [
                    BNGIndexedGeometry(bng_ref, False, geometry)
                    for bng_ref, geometry in zip(bng_refs, intersections)
                ]
            )

        elif part.geom_type == "Polygon":
            # Get the grid square geometries of the BNGReference objects
            bng_geoms = np.array([bng_to_grid_geom(bng_ref) for bng_ref in bng_refs])
            # Prepare the geometry part to speed up contains spatial predicate tests
            prepare(part)
            # Test whether grid square geometries are contained by the geometry part
            bng_bool = contains(part, bng_geoms)
            # Subset bng_refs array based on positive containment
            core = bng_refs[bng_bool]
            # Subset bng_refs array based on negative containment
            edge = bng_refs[~bng_bool]
            # Derive BNGIndexedGeometry objects for core cases and add to the bng_idx_geoms list
            bng_idx_geom_core = [
                BNGIndexedGeometry(bng_ref, True, bng_ref.bng_to_grid_geom())
                for bng_ref in core
            ]
            # Derive the intersection between the part geometry and the 'edge' grid square geometries
            intersections = intersection(part, bng_geoms[~bng_bool])
            # Derive BNGIndexedGeometry objects for 'edge' grid squares and add to the bng_idx_geoms list
            bng_idx_geom_edge = [
                BNGIndexedGeometry(bng_ref, False, geometry)
                for bng_ref, geometry in zip(edge, intersections)
            ]
            # Combine the core and edge BNGIndexedGeometry objects
            bng_idx_geoms.extend(bng_idx_geom_core + bng_idx_geom_edge)

    return bng_idx_geoms
