"""
British National Grid Reference System
--------------------------------------

This module implements a custom British National Grid (BNG) reference 
object for working with geographic locations based on the Ordnance Survey National Grid system. 
The BNG is a map reference system used to identify locations across Great Britain (GB). 
It is designed as a Cartesian grid where positions are identified by a combination of easting and northing 
values within a defined grid square.

The BNG is structured using a hierarchical system of grid squares at various resolutions. 
At its highest level, the grid is divided into 100 km by 100 km squares, 
each of which is identified by a two-letter code. Successive levels of resolution further subdivide 
the grid squares into finer detail, down to individual 1-meter squares.

Grid Reference Structure
------------------------

Each reference consists of a 2-letter prefix (identifying the 100 km grid square), 
followed by an easting and northing value, which may be further subdivided using intermediate resolutions. 
Additionally, an optional suffix representing ordinal (intercardinal) directions (NE, SE, SW, NW) may be 
appended to the reference to account for quadtree subdivision of the grid at finer resolutions. 
The grid reference can be expressed at different scales, as follows:

1. **100 km**: Identified by a two-letter code (e.g. 'TQ').
2. **50 km**: Subdivides the 100 km grid into four quadrants. The grid reference adds an ordinal direction suffix (NE, NW, SE, SW) 
to indicate the quadrant within the 100 km square (e.g. ‘TQSW’).
3. **10 km**: Adds two-digit easting and northing values (e.g. 'TQ23').
4. **5 km**: Subdivides the 10 km square adding an ordinal suffix (e.g. 'TQ53SW').
5. **1 km**: Adds four-digit easting and northing values (e.g. 'TQ2334').
6. **500 m**: Subdivides the 1 km square adding an ordinal suffix (e.g. 'TQ2334NE').
7. **100 m**: Adds six-digit easting and northing values (e.g. ' TQ238347').
8. **50 m**: Subdivides the 100 m square adding an ordinal suffix (e.g. ' TQ238347SE').
9. **10 m**: Adds eight-digit easting and northing values (e.g. ' TQ23863472').
10. **5 m**: Subdivides the 10 m square adding an ordinal suffix (e.g. e.g. ‘TQ23863472NW').
11. **1 m**: Adds ten-digit easting and northing values (e.g. ' TQ2386334729’).



Reference Specification
------------------------

Grid references must adhere to the following format:

- **No spaces** should be used between the components of the reference (i.e. between the 2-letter prefix, 
easting, northing, and ordinal suffix) unless providing a ‘human-readable’ version of the reference.
- The **two-letter 100 km grid square prefixes** and **ordinal direction suffixes** (NE, SE, SW, NW) must always be in **uppercase**.
- For improved human-readability, a single space may be introduced between the 100 km two-letter prefix, 
the numerical components, and ordinal suffix (e.g. ' TQ 2386 3472 SW).
However, note that this format will fail the validation rules in this custom BNG reference object and is 
therefore not allowed in machine-processed grid references.

At each resolution, a given location can be identified with increasing detail, 
allowing for variable accuracy depending on the geospatial application, from small-scale mapping to precise survey measurements.

The BNG system is widely used by the geospatial community across GB. 
This module provides functionality to parse, create, and manipulate BNG references at a range of resolutions.
"""

import re

# Compile regular expression pattern for BNG reference
# Supports the following resolutions: 100km, 50km, 10km, 5km, 1km, 500m, 100m, 50m, 10m, 5m, 1m
_pattern = re.compile(
    r"^[HJNOST][A-HJ-Z](\d{2}|\d{4}|\d{6}|\d{8}|\d{10})?(NE|SE|SW|NW)?$"
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
        >>> is_valid_bng("TQ12")
        True
        >>> is_valid_bng("TQ123")
        False
    """
    return bool(_pattern.match(bng_ref_string))
