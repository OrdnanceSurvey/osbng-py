"""Provides functionality to parse, create and manipulate British National Grid (BNG) references via a custom BNGReference object.

BNGReference Object
------------------------

The BNG index system uses BNG references, also known more simply as grid or tile references, to identify and index locations across 
Great Britain (GB) into grid squares at various resolutions. 

The BNGReference object is a custom class that encapsulates a BNG reference string, providing properties and methods to access 
and manipulate the reference.

British National Grid Index System
------------------------

The Ordnance Survey (OS) BNG index system, also known as the OS National Grid, is a rectangular 
Cartesian 700 x 1300km grid system based upon the transverse Mercator projection. In the BNG, locations 
are specified using coordinates, eastings (x) and northings (y), measured in meters from a defined 
origin point (0, 0) southwest of the Isles of Scilly off the coast of Cornwall, England. Values increase 
to the northeast, covering all of mainland GB and surrounding islands.

The BNG is structured using a hierarchical system of grid squares at various resolutions. At its highest level, 
the grid divides GB into 100 km by 100 km squares, each identified by a two-letter code. Successive levels 
of resolution further subdivide the grid squares into finer detail, down to individual 1-meter squares.

BNG Reference Structure
------------------------

Each BNG reference string consists of a series of alphanumeric characters that encode the easting and northing at 
a given resolution.

A BNG reference includes a 2-letter prefix that identifies the 100 km grid square. This is followed by an 
easting and northing value, and optionally, a suffix indicating an ordinal (intercardinal) direction (NE, SE, SW, NW). 
These suffixes represent a quadtree subdivision of the grid at the 'standard' resolutions (100km, 10km, 1km, 100m, and 10m), 
with each direction indicating a specific quadrant.

<prefix><easting value><northing value><suffix>

There are two exceptions to this structure:

1.  At the 100km resolution, a BNG reference consists only of the prefix.
2.  At the 50km resolution, a BNG reference includes the prefix and the ordinal direction suffix but does not include easting 
or northing components.

A BNG reference can be expressed at different scales, as follows:

1.  100km: Identified by a two-letter code (e.g. 'TQ').
2.  50km: Subdivides the 100 km grid into four quadrants. The grid reference adds an ordinal direction suffix (NE, NW, SE, SW) 
    to indicate the quadrant within the 100 km square (e.g. 'TQ SW').
3.  10km: Adds one-digit easting and northing values (e.g. 'TQ 2 3').
4.  5km: Subdivides the 10 km square adding an ordinal suffix (e.g. 'TQ 53 SW').
5.  1km: Adds two-digit easting and northing values (e.g. 'TQ 23 34').
6.  500m: Subdivides the 1 km square adding an ordinal suffix (e.g. 'TQ 23 34 NE').
7.  100m: Adds three-digit easting and northing values (e.g. ' TQ 238 347').
8.  50m: Subdivides the 100 m square adding an ordinal suffix (e.g. ' TQ 238 347 SE').
9.  10m: Adds four-digit easting and northing values (e.g. ' TQ 2386 3472').
10. 5m: Subdivides the 10 m square adding an ordinal suffix (e.g. 'TQ 2386 3472 NW').
11. 1m: Adds five-digit easting and northing values (e.g. ' TQ 23863 34729').

BNG Reference Formatting
------------------------

BNG reference strings passed to a BNGReference object must adhere to the following format:

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

BNG Reference Application
------------------------

The BNG index system is widely used by the geospatial community across GB. At each resolution, a given location can be identified with 
increasing detail, allowing for variable accuracy depending on the geospatial application, from small-scale mapping to precise 
survey measurements.
"""

import re
from functools import wraps
from shapely.geometry import Polygon, mapping
from typing import Union

from osbng.errors import BNGReferenceError
from osbng.resolution import BNG_RESOLUTIONS

__all__ = ["BNGReference"]

# Compile regular expression pattern for BNG reference string validation
# The geographical extent of the BNG reference system is defined as:
# 0 <= easting < 700000 and 0 <= northing < 1300000
# Supports the following resolutions:
# 100km, 50km, 10km, 5km, 1km, 500m, 100m, 50m, 10m, 5m, 1m
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


def _validate_bng_ref_string(bng_ref_string: str) -> bool:
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
    """Gets the resolution of a BNG reference string in metres.

    Args:
        bng_ref_string (str): The BNG reference string.

    Returns:
        resolution (int): The resolution of the BNG reference in metres.

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
    # and whether an ordinal suffix is present.
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
    """Gets the resolution of a BNG reference expressed as a descriptive string.

    The resolution is returned in a human-readable format, such as '10km', '50km', '5km' etc.

    Args:
        bng_ref_string (str): The BNG reference string.

    Returns:
        str: The resolution of the BNG reference as a string.

    Examples:
        >>> _get_bng_resolution_label("TQ1234")
        '1km'
    """
    # Get the resolution in meters
    resolution_meters = _get_bng_resolution_metres(bng_ref_string)

    # Get the resolution label
    return BNG_RESOLUTIONS.get(resolution_meters)["label"]


def _format_bng_ref_string(bng_ref_string: str) -> str:
    """Returns a pretty formatted BNG reference string.

    Pretty formatting is defined as a single whitespace between the reference components
    including prefix, easting and northing, and suffix if present.

    Args:
        bng_ref_string (str): The BNG reference string.

    Returns:
        pretty_format (str): The pretty formatted BNG reference string.

    Examples:
        >>> _format_bng_ref_string("TQ1234")
        'TQ 12 34'
        >>> _format_bng_ref_string("TQ1234NE")
        'TQ 12 34 NE'
    """
    # Match BNG reference string against regex pattern
    match = _PATTERN.match(bng_ref_string)

    # Extract components of the BNG reference string
    prefix = match.group(1)
    en_components = match.group(2)
    suffix = match.group(3)

    # Pretty format the BNG reference string
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

    Converts a BNG reference string into a BNGReference object, ensuring type consistency
    across the package. All functions accepteding or returning BNG references enforce the use of this class.
    These functions are available both as instance methods of the BNGReference object and as standalone functions,
    providing users with the flexibility to either:

    - Create a BNGReference object and pass it to a function.
    - Create a BNGReference object and use one of its instance methods.

    Args:
        bng_ref_string (str): The BNG reference string.

    Properties:
        bng_ref_compact (str): The BNG reference with whitespace removed.
        bng_ref_formatted (str): The pretty-formatted version of the BNG reference with single spaces between components.
        resolution_metres (int): The resolution of the BNG reference in meters.
        resolution_label (str): The resolution of the BNG reference expressed as a descriptive string.
        __geo_interface__ (dict): A GeoJSON-like mapping for a BNGReference object.

    Methods:
        bng_to_xy(position: str, optional) -> tuple[int | float, int | float]: Returns the easting and northing coordinates for the current BNGReference object.
        bng_to_bbox() -> tuple[int, int, int, int]: Returns bounding box coordinates for the current BNGReference object.
        bng_to_grid_geom() -> Polygon: Returns a grid square as a Shapely Polygon for the current BNGReference object.
        bng_to_children(resolution: int | str | None, optional) -> list[BNGReference]: Returns a list of BNGReference objects that are children of the input BNGReference object.
        bng_to_parent(resolution: int | str | None, optional) -> BNGReference: Returns a BNGReference object that is the parent of the input BNGReference object.

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
        >>> bng_ref.bng_to_xy()
        (512000, 134000)
        >>> bng_ref.bng_to_bbox()
        (512000, 134000, 513000, 135000)
        >>> bng_ref.bng_to_parent()
        BNGReference(bng_ref_formatted=TQ 1 3 SW, resolution_label=5km)
    """

    def __init__(self, bng_ref_string: str):
        # Validate the BNG reference string
        if not _validate_bng_ref_string(bng_ref_string):
            raise BNGReferenceError(f"Invalid BNG reference string: '{bng_ref_string}'")

        # Remove all whitespace for internal storage
        self._bng_ref_compact = bng_ref_string.replace(" ", "")

    @property
    def bng_ref_compact(self) -> str:
        """Returns the BNG reference string with whitespace removed."""
        return self._bng_ref_compact

    @property
    def bng_ref_formatted(self) -> str:
        """Returns a pretty-formatted version of the BNG reference string with single spaces between components."""
        return _format_bng_ref_string(self._bng_ref_compact)

    @property
    def resolution_metres(self) -> int:
        """Returns the resolution of the BNGReference in meters."""
        return _get_bng_resolution_metres(self._bng_ref_compact)

    @property
    def resolution_label(self) -> str:
        """Returns the resolution of the BNGReference expressed as a string."""
        return _get_bng_resolution_label(self._bng_ref_compact)

    @property
    def __geo_interface__(self) -> dict[str, Union[str, dict]]:
        """Returns a GeoJSON-like mapping for a BNGReference object.

        Implements the __geo_interface__ protocol. The returned data structure represents the
        BNGReference object as a GeoJSON-like Feature."""
        return {
            "type": "Feature",
            "properties": {
                "bng_ref": self.bng_ref_compact,
            },
            "geometry": mapping(self.bng_to_grid_geom()),
        }

    def __eq__(self, other):
        if isinstance(other, BNGReference):
            return self.bng_ref_compact == other.bng_ref_compact
        return False

    def __hash__(self):
        return hash(self.bng_ref_compact)

    def __repr__(self):
        return f"BNGReference(bng_ref_formatted={self.bng_ref_formatted}, resolution_label={self.resolution_label})"

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

    def bng_to_children(
        self, resolution: int | str | None = None
    ) -> list["BNGReference"]:
        """Returns a list of BNGReference objects that are children of the current BNGReference object.

        By default, the children of the BNGReference object is defined as the BNGReference objects in the
        next resolution down from the input BNGReference resolution. For example, 100km -> 50km.

        Any valid resolution can be provided as the child resolution, provided it is less than the
        resolution of the input BNGReference.

        Args:
            resolution (int | str | None, optional): The resolution of the children BNGReference objects. Defaults to None.

        Returns:
            list[BNGReference]: A list of BNGReference objects that are children of the current BNGReference object.

        Raises:
            BNGHierarchyError: If the resolution of the current BNGReference object is 1m.
            BNGHierarchyError: If the resolution is greater than or equal to the resolution of the current BNGReference object.
            BNGResolutionError: If an invalid resolution is provided.

        Examples:
            >>> BNGReference("SU").bng_to_children()
            [BNGReference(bng_ref_formatted=SU SW, resolution_label=50km),
            BNGReference(bng_ref_formatted=SU SE, resolution_label=50km),
            BNGReference(bng_ref_formatted=SU NW, resolution_label=50km),
            BNGReference(bng_ref_formatted=SU NE, resolution_label=50km)]
            >>> BNGReference("SU36").bng_to_children()
            [BNGReference(bng_ref_formatted=SU 3 6 SW, resolution_label=5km),
            BNGReference(bng_ref_formatted=SU 3 6 SE, resolution_label=5km),
            BNGReference(bng_ref_formatted=SU 3 6 NW, resolution_label=5km),
            BNGReference(bng_ref_formatted=SU 3 6 NE, resolution_label=5km)]
        """

        from osbng.hierarchy import bng_to_children as _bng_to_children

        return _bng_to_children(self, resolution)

    def bng_to_parent(self, resolution: int | str | None = None) -> "BNGReference":
        """Returns a BNGReference object that is the parent of the current BNGReference object.

        By default, the parent of the BNGReference object is defined as the BNGReference in the next BNG
        resolution up from the current BNGReference resolution. For example, 50km -> 100km.

        Any valid resolution can be provided as the parent resolution, provided it is greater than the
        resolution of the current BNGReference.

        Args:
            resolution (int | str | None, optional): The resolution of the parent BNGReference. Defaults to None.

        Returns:
            BNGReference: A BNGReference object that is the parent of the current BNGReference object.

        Raises:
            BNGHierarchyError: If the resolution of the current BNGReference object is 100km.
            BNGHierarchyError: If the resolution is less than or equal to the resolution of the current BNGReference object.
            BNGResolutionError: If an invalid resolution is provided.

        Examples:
            >>> BNGReference("SU 3 6 SW").bng_to_parent()
            BNGReference(bng_ref_formatted=SU 3 6, resolution_label=10km)
            >>> BNGReference("SU 342 567").bng_to_parent()
            BNGReference(bng_ref_formatted=SU 34 56 NW, resolution_label=500m)
            >>> bng_to_parent(BNGReference("SU 342 567"), resolution=10000)
            BNGReference(bng_ref_formatted=SU 3 5, resolution_label=10km)

        """

        from osbng.hierarchy import bng_to_parent as _bng_to_parent

        return _bng_to_parent(self, resolution)
    
    def bng_kring(self, k: int, return_relations: bool = False) -> list["BNGReference"]:
        """Returns a list of BNG reference objects representing a hollow ring around the current BNG reference object
        at a grid distance k.

        Returned BNG reference objects are ordered North to South then West to East, therefore not in ring order.

        Args:
            k (int): Grid distance in units of grid squares.

        Kwargs:
            return_relations (bool): If True, returns a list of (BNGReference, dx, dy) tuples where dx, dy are integer offsets in 
                grid units.  If False (default), returns a list of BNGReference objects.

        Returns:
            list[BNGReference]: All BNGReference objects representing squares in a square ring of radius k.

        Examples:
            >>> BNGReference("SU1234").bng_kring(1)
            [BNGReference(bng_ref_formatted=SU 11 33, resolution_label=1km), BNGReference(bng_ref_formatted=SU 12 33, resolution_label=1km),
            BNGReference(bng_ref_formatted=SU 13 33, resolution_label=1km), BNGReference(bng_ref_formatted=SU 11 34, resolution_label=1km),
            BNGReference(bng_ref_formatted=SU 13 34, resolution_label=1km), BNGReference(bng_ref_formatted=SU 11 35, resolution_label=1km),
            BNGReference(bng_ref_formatted=SU 12 35, resolution_label=1km), BNGReference(bng_ref_formatted=SU 13 35, resolution_label=1km)]
            >>> BNGReference("SU1234").bng_kring(3)
            [list of 24 BNGReference objects]
        """

        from osbng.traversal import bng_kring as _bng_kring

        return _bng_kring(self, k, return_relations=return_relations)
    
    def bng_kdisc(self, k: int, return_relations: bool = False) -> list["BNGReference"]:
        """Returns a list of BNG reference objects representing a filled disc around the current BNG reference object
        up to a grid distance k, including the given central BNG reference object.

        Returned BNG reference objects are ordered North to South then West to East.

        Args:
            k (int): Grid distance in units of grid squares.

        Kwargs:
            return_relations (bool): If True, returns a list of (BNGReference, dx, dy) tuples where dx, dy are integer offsets in 
                grid units.  If False (default), returns a list of BNGReference objects.

        Returns:
            list[BNGReference]: All BNGReference objects representing grid squares in a square of radius k.

        Examples:
            >>> BNGReference("SU1234").bng_kdisc(1)
            [BNGReference(bng_ref_formatted=SU 11 33, resolution_label=1km), BNGReference(bng_ref_formatted=SU 12 33, resolution_label=1km),
            BNGReference(bng_ref_formatted=SU 13 33, resolution_label=1km), BNGReference(bng_ref_formatted=SU 11 34, resolution_label=1km),
            BNGReference(bng_ref_formatted=SU 12 34, resolution_label=1km), BNGReference(bng_ref_formatted=SU 13 34, resolution_label=1km),
            BNGReference(bng_ref_formatted=SU 11 35, resolution_label=1km), BNGReference(bng_ref_formatted=SU 12 35, resolution_label=1km),
            BNGReference(bng_ref_formatted=SU 13 35, resolution_label=1km)]
            >>> BNGReference("SU1234").bng_kdisc(3)
            [list of 49 BNGReference objects]
        """

        from osbng.traversal import bng_kdisc as _bng_kdisc

        return _bng_kdisc(self, k, return_relations=return_relations)
    
    def bng_distance(self, bng_ref2: "BNGReference", edge_to_edge: bool = False) -> float:
        """Returns the euclidean distance between the centroids of the current BNGReference object and another.
        Note that the other BNGReference object does not necessarily need to share a common resolution.

        Args:
            bng_ref2 (BNGReference): A BNGReference object.

        Kwargs:
            edge_to_edge (bool): If False (default), distance will be centroid-to-centroid distance.
                If True, distance will be the shortest distance between any point in the grid squares.

        Returns:
            float: The euclidean distance between the centroids of the two BNGReference objects.

        Raises:
            TypeError: If the bng_ref2 argument is not a BNGReference object.

        Examples:
            >>> BNGReference("SE1433").bng_distance(BNGRerence("SE1533"))
            1000.0
            >>> BNGReference("SE1433").bng_distance(BNGRerence("SE1631"))
            2828.42712474619
            >>> BNGReference("SE1433").bng_distance(BNGRerence("SE"))
            39147.158262126766
            >>> BNGReference("SE1433").bng_distance(BNGRerence("SENW"))
            42807.709586007986
            >>> BNGReference("SE").bng_distance(BNGRerence("OV"))
            141421.35623730952
        """

        from osbng.traversal import bng_distance as _bng_distance

        return _bng_distance(self, bng_ref2, edge_to_edge=edge_to_edge)
    
    def bng_neighbours(self):
        """Returns a list of BNGReference objects representing the four neighbouring grid squares
        sharing an edge with the current BNGReference.

        Returns:
            list[BNGReference]: The grid squares immediately North, South, East and West of bng_ref.

        Examples:
            >>> BNGRefence("SU1234").bng_neighbours()
            [BNGReference('SU1235'), BNGReference('SU1334'), BNGReference('SU1233'), BNGReference('SU1134')]
        """

        from osbng.traversal import bng_neighbours as _bng_neighbours

        return _bng_neighbours(self)
    
    def bng_is_neighbour(self, bng_ref2: "BNGReference") -> bool:
        """Returns True if the BNGReference object is a neighbour, otherwise False.
        Neighbours are defined as grid squares that share an edge with the current BNGReference object.

        Args:
            bng_ref2 (BNGReference): A BNGReference object.

        Returns:
            bool: True if the two BNGReference objects are neighbours, otherwise False.

        Raises:
            TypeError: If the bng_ref2 argument is not a BNGReference object.
            BNGNeighbourError: If the BNGReference object is not at the same resolution.

        Examples:
            >>> BNGReference("SE1921").bng_is_neighbour(BNGReference("SE1821"))
            True
            >>> BNGReference("SE1922").bng_is_neighbour(BNGReference("SE1821"))
            False
            >>> BNGReference("SU1234").bng_is_neighbour(BNGReference("SU1234"))
            False

        """

        from osbng.traversal import bng_is_neighbour as _bng_is_neighbour

        return _bng_is_neighbour(self, bng_ref2)
    
    def bng_dwithin(self, d: int | float) -> list["BNGReference"]:
        """Returns a list of BNG reference objects around the current BNG reference object within an absolute distance d.
        All squares will be returned for which any part of its boundary is within distance d of any part of
        the BNGReference object's boundary.

        Args:
            d (int or float): The absolute distance d in metres.

        Returns:
            list[BNGReference]: All grid squares which have any part of their geometry within distance
                d of the current grid square

        Examples:
            >>> BNGReference("SU1234").bng_dwithin(1000)
            [BNGReference(bng_ref_formatted=SU 11 33, resolution_label=1km), BNGReference(bng_ref_formatted=SU 12 33, resolution_label=1km),
            BNGReference(bng_ref_formatted=SU 13 33, resolution_label=1km), BNGReference(bng_ref_formatted=SU 11 34, resolution_label=1km),
            BNGReference(bng_ref_formatted=SU 12 34, resolution_label=1km), BNGReference(bng_ref_formatted=SU 13 34, resolution_label=1km),
            BNGReference(bng_ref_formatted=SU 11 35, resolution_label=1km), BNGReference(bng_ref_formatted=SU 12 35, resolution_label=1km),
            BNGReference(bng_ref_formatted=SU 13 35, resolution_label=1km)]
            >>> BNGReference("SU1234").bng_dwithin(1001)
            [list of 21 BNGReference objects]
        """

        from osbng.traversal import bng_dwithin as _bng_dwithin

        return _bng_dwithin(self, d)


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
