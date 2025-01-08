"""British National Grid Reference System.

Implements a custom British National Grid (BNG) reference object for working with geographic 
locations based on the Ordnance Survey (OS) National Grid system. 

The BNG is a rectangular Cartesian 700 x 1300km grid system based upon the transverse Mercator 
projection used to identify locations across Great Britain (GB). In the BNG, locations are specified 
using coordinates (eastings and northings). These coordinates are measured in meters from a defined 
origin point (0, 0) southwest of the Isles of Scilly. Values increase to the northeast, covering all 
of mainland Great Britain and surrounding islands.

The BNG is structured using a hierarchical system of grid squares at various resolutions. At its highest level, 
the grid divides GB into 100 km by 100 km squares, each identified by a two-letter code. Successive levels 
of resolution further subdivide the grid squares into finer detail, down to individual 1-meter squares.

BNG Reference Structure
------------------------

Each BNG reference includes a 2-letter prefix that identifies the 100 km grid square. This is followed by an 
easting and northing value, and optionally, a suffix indicating ordinal (intercardinal) directions (NE, SE, SW, NW). 
These suffixes represent a quadtree subdivision of the grid at the 'standard' resolutions (100 km, 10 km, 1 km, 100 m, and 10 m), 
with each direction indicating a specific quadrant.

There are two exceptions to this structure:

1.  At the 100 km resolution, the reference consists only of the prefix.
2.  At the 50 km resolution, the reference includes the prefix and the ordinal direction suffix but does not include easting 
or northing components.

A BNG reference can be expressed at different scales, as follows:
1.  100 km: Identified by a two-letter code (e.g. 'TQ').
2.  50 km: Subdivides the 100 km grid into four quadrants. The grid reference adds an ordinal direction suffix (NE, NW, SE, SW) 
to indicate the quadrant within the 100 km square (e.g. 'TQ SW').
3.  10 km: Adds one-digit easting and northing values (e.g. 'TQ 2 3').
4.  5 km: Subdivides the 10 km square adding an ordinal suffix (e.g. 'TQ 53 SW').
5.  1 km: Adds two-digit easting and northing values (e.g. 'TQ 23 34').
6.  500 m: Subdivides the 1 km square adding an ordinal suffix (e.g. 'TQ 23 34 NE').
7.  100 m: Adds three-digit easting and northing values (e.g. ' TQ 238 347').
8.  50 m: Subdivides the 100 m square adding an ordinal suffix (e.g. ' TQ 238 347 SE').
9.  10 m: Adds four-digit easting and northing values (e.g. ' TQ 2386 3472').
10. 5 m: Subdivides the 10 m square adding an ordinal suffix (e.g. 'TQ 2386 3472 NW').
11. 1 m: Adds five-digit easting and northing values (e.g. ' TQ 23863 34729').

BNG Reference Specification
------------------------

User-defined input BNG reference strings must adhere to the following format:

- Whitespace may or may not separate the components of the reference (i.e. between the two-letter 100km grid square prefix, easting, 
northing, and ordinal suffix).
- If whitespace is present, it should be a single space character.
- Whitespace can be inconsistently used between components of the reference.
- The two-letter 100 km grid square prefixes and ordinal direction suffixes (NE, SE, SW, NW) should be capitalised.

EPSG:27700 (OSGB36 / British National Grid)
------------------------

The BNG system is a practical application of the EPSG:27700 (OSGB36 / British National Grid) coordinate reference system 
(https://epsg.io/27700) which provides the geodetic framework that defines how locations defined by easting and northing coordinates 
and encoded as BNG references (e.g. 'ST 569 714') are projected to the grid.

Application
------------------------

The BNG system is widely used by the geospatial community across GB. At each resolution, a given location can be identified with 
increasing detail, allowing for variable accuracy depending on the geospatial application, from small-scale mapping to precise 
survey measurements.

This module provides functionality to parse, create and manipulate BNG references at a range of resolutions.
"""

import re
from functools import wraps
from shapely.geometry import Polygon

from osbng.resolution import _RESOLUTION_TO_STRING
from osbng.errors import BNGReferenceError

# Compile regular expression pattern for BNG reference
# The geographical extent of the BNG reference system is defined as:
# easting >= 0 and easting < 700000 and northing >= 0 and northing < 1300000
# Supports the following resolutions: 100km, 50km, 10km, 5km, 1km, 500m, 100m, 50m, 10m, 5m, 1m
_PATTERN = re.compile(
    r"""
    ^
    # 100km grid square prefix
    (H[LMNOPQRSTUVWXYZ]|
     N[ABCDEFGHJKLMNOPQRSTUVWXYZ]|
     O[ABFGLMQRVW]|
     S[ABCDEFGHJKLMNOPQRSTUVWXYZ]|
     T[ABFGLMQRVW]|
     J[LMQRVW])
    # Zero or one whitespace characters
    \s?
    # Easting and northing coordinates
    # 2-8 digit BNG reference
    # Not separated by whitespace
    (?:(\d{2}|\d{4}|\d{6}|\d{8}|
    # Separated by whitespace
    \d{1}\s\d{1}|\d{2}\s\d{2}|\d{3}\s\d{3}|\d{4}\s\d{4}|
    # 10-digit BNG reference
    # Not separated by whitespace
    \d{10}$|
    # Separated by whitespace
    \d{5}\s\d{5}$))?
    # Zero or one whitespace characters
    \s?
    # Ordinal direction suffix
    (NE|SE|SW|NW)?$""",
    re.VERBOSE,
)


def _validate_bng(bng_ref_string: str) -> bool:
    """Validates a BNG reference string using a regular expression pattern.

    Args:
        bng_ref_string (str): The BNG reference string to validate.

    Returns:
        bool: True if the BNG reference is valid, False otherwise.

    Examples:
        >>> _validate_bng("TQ 12 34")
        True
        >>> _validate_bng("TQ1234")
        True
        >>> _validate_bng("tq123")
        False
    """
    return bool(_PATTERN.match(bng_ref_string))


def _get_bng_resolution_metres(bng_ref_string: str) -> int:
    """Gets the resolution of a BNG reference string in meters.

    The resolution is determined based on the length of the easting
    and northing components and whether an ordinal suffix is present.

    Args:
        bng_ref_string (str): The BNG reference string.

    Returns:
        resolution (int): The resolution of the BNG reference in meters.

    Examples:
        >>> _get_bng_resolution_metres("TQ1234")
        1000
    """
    # Match BNG reference string against regex pattern
    match = _PATTERN.match(bng_ref_string)

    # Extract components of the BNG reference
    en_components = match.group(2)
    suffix = match.group(3)

    # Determine resolution based on length of easting and northing components
    if en_components is None:
        resolution = 100000
    else:
        length = len(en_components)
        # The possible resolutions are powers of ten: 1, 10, 100, 1000, 10000, 100000
        # Integer division by 2 to determine the appropriate power of ten
        # Subtracting from 5 aligns the length with the correct power of ten
        resolution = 10 ** (5 - length // 2)

    # Adjust for ordinal suffix if present
    if suffix:
        resolution //= 2  # Ordinal suffix halves the resolution

    return resolution


def _get_bng_resolution_label(bng_ref_string: str) -> str:
    """Gets the resolution of a BNG reference expressed as a string.

    The resolution is returned in a human-readable format, such as '10km', '50km', etc.

    Args:
        bng_ref_string (str): The BNG reference string.

    Returns:
        str: The resolution of the BNG reference as a string.

    Examples:
        >>> _get_bng_resolution_label("TQ1234")
        '1km'
    """
    resolution_meters = _get_bng_resolution_metres(bng_ref_string)

    return _RESOLUTION_TO_STRING.get(resolution_meters)["label"]


def _get_bng_pretty_format(bng_ref_string: str) -> str:
    """Parses a BNG reference string and returns a pretty formatted BNG reference.

    Pretty formatting is defined as a single whitespace between the reference components
    including prefix, easting and northing, and suffix.

    Args:
        bng_ref_string (str): The BNG reference string.

    Returns:
        pretty_format (str): The pretty formatted BNG reference.

    Examples:
        >>> _get_bng_pretty_format("TQ1234")
        'TQ 12 34'
        >>> _get_bng_pretty_format("TQ1234NE")
        'TQ 12 34 NE'
    """
    # Match BNG reference string against regex pattern
    match = _PATTERN.match(bng_ref_string)

    # Extract components of the BNG reference
    prefix = match.group(1)
    en_components = match.group(2)
    suffix = match.group(3)

    # Pretty format the BNG reference
    if en_components is None:
        pretty_format = prefix
    else:
        # Split easting and northing components
        length = len(en_components)
        easting = en_components[: length // 2]
        northing = en_components[length // 2 :]
        # Add whitespace between components
        pretty_format = f"{prefix} {easting} {northing}"

    # Add ordinal suffix if present
    if suffix:
        pretty_format += f" {suffix}"

    return pretty_format


class BNGReference:
    """A custom object for handling British National Grid (BNG) references.

    Converts a BNG reference string into a BNG reference object.

    Args:
        bng_ref_string (str): The BNG reference string.

    Properties:
        bng_ref_compact (str): The BNG reference with whitespace removed.
        bng_ref_formatted (str): The pretty-formatted version of the BNG reference with single spaces between components.
        resolution_metres (int): The resolution of the BNG reference in meters.
        resolution_label (str): The resolution of the BNG reference expressed as a descriptive string.

    Raises:
        BNGReferenceError: If the BNG reference string is invalid.

    Examples:
        >>> bng_ref = BNGReference("TQ1234")
        >>> bng_ref.bng_ref_compact
        'TQ1234'
        >>> bng_ref.bng_ref_formatted
        'TQ 12 34'
        >>> bng_ref.resolution_metres
        1000
        >>> bng_ref.resolution_label
        '1km'
    """

    def __init__(self, bng_ref_string: str):
        # Validate the BNG reference string
        if not _validate_bng(bng_ref_string):
            raise BNGReferenceError(f"Invalid BNG reference: '{bng_ref_string}'")

        # Remove all whitespace for internal storage
        self._bng_ref_compact = bng_ref_string.replace(" ", "")

    @property
    def bng_ref_compact(self) -> str:
        """Returns the BNG reference with whitespace removed."""
        return self._bng_ref_compact

    @property
    def bng_ref_formatted(self) -> str:
        """Returns a pretty-formatted version of the BNG reference with single spaces between components."""
        return _get_bng_pretty_format(self._bng_ref_compact)

    @property
    def resolution_metres(self) -> int:
        """Returns the resolution of the BNG reference in meters."""
        return _get_bng_resolution_metres(self._bng_ref_compact)

    @property
    def resolution_label(self) -> str:
        """Returns the resolution of the BNG reference expressed as a string."""
        return _get_bng_resolution_label(self._bng_ref_compact)

    def bng_to_xy(
        self, position: str = "lower-left"
    ) -> tuple[int | float, int | float]:
        """Returns the easting and northing coordinates for the current BNGReference object, at a specified grid cell position.

        Args:
            position (str): The grid cell position expressed as a string.
                            One of: 'lower-left', 'upper-left', 'upper-right', 'lower-right', 'centre'.

        Returns:
            tuple[int | float, int | float]: The easting and northing coordinates as a tuple.

        Raises:
            ValueError: If invalid position provided.

        Example:
            >>> BNGReference("SU").bng_to_xy("lower-left")
            (400000, 100000)
            >>> BNGReference("SU 3 1").bng_to_xy("lower-left")
            (430000, 110000)
            >>> BNGReference("SU 3 1 NE").bng_to_xy("centre")
            (437500, 117500)
            >>> BNGReference("SU 37289 15541").bng_to_xy("centre")
            (437289.5, 115541.5)
        """
        from osbng.indexing import bng_to_xy as _bng_to_xy

        return _bng_to_xy(self, position)

    def bng_to_bbox(self) -> tuple[int, int, int, int]:
        """Returns bounding box coordinates for the current BNGReference object.

        Returns:
            tuple[int, int, int, int]: The bounding box coordinates (min x, min y, max x, max y) as a tuple.

        Example:
            >>> BNGReference("SU").bng_to_bbox()
            (400000, 100000, 500000, 200000)
            >>> BNGReference("SU 3 1").bng_to_bbox()
            (430000, 110000, 440000, 120000)
            >>> BNGReference("SU 3 1 NE").bng_to_bbox()
            (435000, 115000, 440000, 120000)
            >>> BNGReference("SU 37289 15541").bng_to_bbox()
            (437289, 115541, 437290, 115542)
        """
        from osbng.indexing import bng_to_bbox as _bng_to_bbox

        return _bng_to_bbox(self)

    def bng_to_grid_geom(self) -> Polygon:
        """Returns a grid square as a Shapely Polygon for the current BNGReference object.

        Returns:
            Polygon: Grid square as Shapely Polygon object.

        Example:
            >>> BNGReference("SU").bng_to_grid_geom().wkt
            'POLYGON ((500000 100000, 500000 200000, 400000 200000, 400000 100000, 500000 100000))'
            >>> BNGReference("SU 3 1").bng_to_grid_geom().wkt
            'POLYGON ((440000 110000, 440000 120000, 430000 120000, 430000 110000, 440000 110000))'
            >>> BNGReference("SU 3 1 NE").bng_to_grid_geom().wkt
            'POLYGON ((440000 115000, 440000 120000, 435000 120000, 435000 115000, 440000 115000))'
            >>> BNGReference("SU 37289 15541").bng_to_grid_geom().wkt
            'POLYGON ((437290 115541, 437290 115542, 437289 115542, 437289 115541, 437290 115541))'
        """
        from osbng.indexing import bng_to_grid_geom as _bng_to_grid_geom

        return _bng_to_grid_geom(self)


def _validate_bngreference(func):
    """Decorator to validate that the first positional argument of a function is a BNGReference object."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        if not isinstance(args[0], BNGReference):
            raise TypeError(
                f"First argument must be a BNGReference object, got: {type(args[0])}"
            )
        return func(*args, **kwargs)

    return wrapper
