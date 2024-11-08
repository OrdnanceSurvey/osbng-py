"""British National Grid Reference System.

This module implements a custom British National Grid (BNG) reference 
object for working with geographic locations based on the Ordnance Survey National Grid system. 
The BNG is a map reference system used to identify locations across Great Britain (GB). 
It is designed as a Cartesian grid where positions are identified by a combination of (positive) easting and northing 
values within a defined grid square.
The origin point (0, 0) of the BNG system is located to the southwest of the Isles of Scilly.

The BNG is structured using a hierarchical system of grid squares at various resolutions. 
At its highest level, the grid is divided into 100 km by 100 km squares, 
each of which is identified by a two-letter code. Successive levels of resolution further subdivide 
the grid squares into finer detail, down to individual 1-meter squares.

BNG Reference Structure
------------------------

Each reference consists of a 2-letter prefix (identifying the 100 km grid square), 
followed by an easting and northing value, which may be further subdivided using intermediate resolutions. 
Additionally, an optional suffix representing ordinal (intercardinal) directions (NE, SE, SW, NW) may be 
appended to the reference to account for quadtree subdivision of the grid at finer resolutions. 
The grid reference can be expressed at different scales, as follows:

1. 100 km: Identified by a two-letter code (e.g. 'TQ').
2. 50 km: Subdivides the 100 km grid into four quadrants. The grid reference adds an ordinal direction suffix (NE, NW, SE, SW) 
to indicate the quadrant within the 100 km square (e.g. 'TQ SW').
3. 10 km: Adds one-digit easting and northing values (e.g. 'TQ 2 3').
4. 5 km: Subdivides the 10 km square adding an ordinal suffix (e.g. 'TQ 53 SW').
5. 1 km: Adds two-digit easting and northing values (e.g. 'TQ 23 34').
6. 500 m: Subdivides the 1 km square adding an ordinal suffix (e.g. 'TQ 23 34 NE').
7. 100 m: Adds three-digit easting and northing values (e.g. ' TQ 238 347').
8. 50 m: Subdivides the 100 m square adding an ordinal suffix (e.g. ' TQ 238 347 SE').
9. 10 m: Adds four-digit easting and northing values (e.g. ' TQ 2386 3472').
10. 5 m: Subdivides the 10 m square adding an ordinal suffix (e.g. 'TQ 2386 3472 NW').
11. 1 m: Adds five-digit easting and northing values (e.g. ' TQ 23863 34729').

Reference Specification
------------------------

BNG references must adhere to the following format:

- Whitespace may or may not separate  the components of the reference (i.e. between the two-letter 100km grid square prefix, 
easting, northing, and ordinal suffix).
- If whitespace is present, it should be a single space character.
- Whitespace can be inconsistently used between components of the reference.
- The two-letter 100 km grid square prefixes and ordinal direction suffixes (NE, SE, SW, NW) should be capitalised.

At each resolution, a given location can be identified with increasing detail, 
allowing for variable accuracy depending on the geospatial application, from small-scale mapping to precise survey measurements.

The BNG system is widely used by the geospatial community across GB. 
This module provides functionality to parse, create and manipulate BNG references at a range of resolutions.
"""

import re

# Compile regular expression pattern for BNG reference
# The geographical extent of the BNG reference system is defined as:
# easting >= 0 and easting < 700000 and northing >= 0 and northing < 1300000
# Supports the following resolutions: 100km, 50km, 10km, 5km, 1km, 500m, 100m, 50m, 10m, 5m, 1m
_pattern = re.compile(
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

# BNG resolution mappings from metres to string representations
_resolution_to_string = {
    100000: "100km",
    50000: "50km",
    10000: "10km",
    5000: "5km",
    1000: "1km",
    500: "500m",
    100: "100m",
    50: "50m",
    10: "10m",
    5: "5m",
    1: "1m",
}


def is_valid_bng(bng_ref_string: str) -> bool:
    """Validates a BNG reference string using a regular expression pattern.

    Args:
        bng_ref_string (str): The BNG reference string to validate.

    Returns:
        bool: True if the BNG reference is valid, False otherwise.

    Examples:
        >>> is_valid_bng("TQ 12 34")
        True
        >>> is_valid_bng("TQ1234")
        True
        >>> is_valid_bng("tq123")
        False
    """
    return bool(_pattern.match(bng_ref_string))
