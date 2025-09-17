"""Provides functionality to manipulate British National Grid (BNG) references.

----------------------
BNGReference Object
----------------------

The BNG index system uses BNG references, also known more simply as grid or tile
references, to identify and index locations across Great Britain (GB) into grid squares
at various resolutions.

The :class:`~osbng.bng_reference.BNGReference` object is a custom class that
encapsulates a BNG reference string, providing properties and methods to access
and manipulate the reference.

---------------------------------------
British National Grid Index System
---------------------------------------

The Ordnance Survey (OS) BNG index system, also known as the OS National Grid, is a
rectangular Cartesian 700 x 1300km grid system based upon the transverse Mercator
projection. In the BNG, locations are specified using coordinates, ``eastings (x)`` and
``northings (y)``, measured in meters from a defined origin point (0, 0) southwest of
the Isles of Scilly off the coast of Cornwall, England. Values increase to the
northeast, covering all of mainland GB and surrounding islands.

The BNG is structured using a hierarchical system of grid squares at various
resolutions. At its highest level, the grid divides GB into 100km by 100km squares,
each identified by a two-letter code. Successive levels of resolution further subdivide
the grid squares into finer detail, down to individual 1-meter squares.

.. image:: https://raw.githubusercontent.com/OrdnanceSurvey/osbng-py/main/docs/_static/images/osbng_grids_100km.png
   :align: center

---------------------------
BNG Reference Structure
---------------------------

Each BNG reference string consists of a series of alphanumeric characters that encode
the easting and northing at a given resolution.

A BNG reference includes a 2-letter prefix that identifies the 100km grid square. This
is followed by an easting and northing value, and optionally, a suffix indicating an
ordinal (intercardinal) direction (``NE``, ``SE``, ``SW``, ``NW``). These suffixes
represent a quadtree subdivision of the grid at the 'standard' resolutions (``100km``,
``10km``, ``1km``, ``100m``, and ``10m``), with each direction indicating a specific
quadrant.::

<prefix><easting value><northing value><suffix>

There are two exceptions to this structure:

1.  At the 100km resolution, a BNG reference consists only of the prefix.
2.  At the 50km resolution, a BNG reference includes the prefix and the ordinal
    direction suffix but does not include easting or northing components.

A BNG reference can be expressed at different scales, as follows:

=========== ========================================================= ==================
Resolution   Description                                               Example
=========== ========================================================= ==================
100km        Identified by a two-letter code                           TQ
50km         Subdivides the 100km grid into four quadrants. The grid   TQ SW
             reference adds an ordinal direction suffix
             (NE, NW, SE, SW) to indicate the quadrant within the
             100km square.
10km         Adds one-digit easting and northing values                TQ 2 3
5km          Subdivides the 10km square adding an ordinal suffix       TQ 23 SW
1km          Adds two-digit easting and northing values                TQ 23 34
500m         Subdivides the 1km square adding an ordinal suffix        TQ 23 34 NE
100m         Adds three-digit easting and northing values              TQ 238 347
50m          Subdivides the 100m square adding an ordinal suffix       TQ 238 347 SE
10m          Adds four-digit easting and northing values               TQ 2386 3472
5m           Subdivides the 10m square adding an ordinal suffix        TQ 2386 3472 NW
1m           Adds five-digit easting and northing values               TQ 23863 34729
=========== ========================================================= ==================

---------------------------
BNG Reference Formatting
---------------------------

BNG reference strings passed to a :class:`~osbng.bng_reference.BNGReference` object must
adhere to the following format:

- Whitespace may or may not separate the components of the reference (i.e. between the
  two-letter 100km grid square prefix, easting, northing, and ordinal suffix).
- If whitespace is present, it should be a single space character.
- Whitespace can be inconsistently used between components of the reference.
- The two-letter 100km grid square prefixes and ordinal direction suffixes
  (``NE``, ``SE``, ``SW``, ``NW``) should be capitalised.

-----------------------------------------------
  EPSG:27700 (OSGB36 / British National Grid)
-----------------------------------------------

The BNG system is a practical application of the `EPSG:27700 (OSGB36 / British National
Grid) <https://epsg.io/27700>`__ coordinate reference system which provides the geodetic
framework that defines how locations defined by easting and northing coordinates and
encoded as BNG references (e.g. 'ST 569 714') are projected to the grid.

----------------------------
BNG Reference Application
----------------------------

The BNG index system is widely used by the geospatial community across GB. At each
resolution, a given location can be identified with increasing detail, allowing for
variable accuracy depending on the geospatial application, from small-scale mapping to
precise survey measurements.
"""

import inspect
import re
from functools import wraps
from typing import Callable, Union

from shapely.geometry import Polygon, mapping

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
    """Returns the resolution of a BNG reference string in metres.

    Args:
        bng_ref_string (str): The BNG reference string.

    Returns:
        resolution (int): The resolution of the BNG reference in metres.

    Examples:
        >>> _get_bng_resolution_metres("TQ1234")
        1000
        >>> _get_bng_resolution_metres("TQ12")
        10000
        >>> _get_bng_resolution_metres("TQSW")
        50000
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
    """Returns the resolution of a BNG reference string as a descriptive label.

    The resolution is returned in a human-readable format, such as '10km', '50km', '5km'
    etc.

    Args:
        bng_ref_string (str): The BNG reference string.

    Returns:
        str: The resolution of the BNG reference as a string label.

    Examples:
        >>> _get_bng_resolution_label("TQ1234")
        '1km'
        >>> _get_bng_resolution_label("TQ12")
        '10km'
        >>> _get_bng_resolution_label("TQSW")
        '50km'
    """
    # Get the resolution in meters
    resolution_meters = _get_bng_resolution_metres(bng_ref_string)

    # Get the resolution label
    return BNG_RESOLUTIONS.get(resolution_meters)["label"]


def _format_bng_ref_string(bng_ref_string: str) -> str:
    """Returns a BNG reference string in pretty format.

    Uses a single space between the prefix, easting, northing, and suffix to improve
    readability.

    Args:
        bng_ref_string (str): The BNG reference string.

    Returns:
        pretty_format (str): The pretty formatted BNG reference string.

    Examples:
        >>> _format_bng_ref_string("TQ1234")
        'TQ 12 34'
        >>> _format_bng_ref_string("TQ1234NE")
        'TQ 12 34 NE'
        >>> _format_bng_ref_string("TQ127349NE")
        'TQ 127 349 NE'
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
    """A custom object for handling BNG references.

    Converts a BNG reference string into a :class:`~osbng.bng_reference.BNGReference`
    object, ensuring type consistency across the package. All functions accepting or
    returning BNG references enforce the use of this class.

    These functions are available both as instance methods of the
    :class:`~osbng.bng_reference.BNGReference` object and as standalone functions,
    providing users with the flexibility to either:

    - Create a :class:`~osbng.bng_reference.BNGReference` object and pass it to a
      function.
    - Create a :class:`~osbng.bng_reference.BNGReference` object and use one of its
      instance methods.

    Args:
        bng_ref_string (str): The BNG reference string.

    Attributes:
        bng_ref_compact (str): The BNG reference string of this ``BNGReference`` with
            whitespace removed.
        bng_ref_formatted (str): The pretty-formatted BNG reference string of this
            ``BNGReference`` with single spaces between components.
        resolution_metres (int): The resolution of this ``BNGReference`` in meters.
        resolution_label (str): The resolution of this ``BNGReference`` expressed as a
            descriptive string.
        __geo_interface__ (dict): A GeoJSON-like mapping of this ``BNGReference``.

    Methods:
        bng_to_xy(position: str = "lower-left") -> tuple[int | float, int | float]:
            Returns easting and northing coordinates of this  ``BNGReference`` at a
            specified grid square position.
        bng_to_bbox() -> tuple[int, int, int, int]: Returns grid square bounding box
            coordinates of this ``BNGReference``.
        bng_to_grid_geom() -> Polygon: Returns a grid square as a ``Shapely Polygon``
            of this ``BNGReference``.
        bng_to_children(resolution: int | str | None = None) -> list[BNGReference]:
            Returns a list of ``BNGReference`` objects that are children of this
            ``BNGReference``.
        bng_to_parent(resolution: int | str | None = None) -> BNGReference: Returns the
            ``BNGReference`` that is the parent of this ``BNGReference``.
        bng_kring(k: int, return_relations: bool = False) -> list[BNGReference] |
            list[tuple[BNGReference, int, int]]:
            Returns a list of ``BNGReference`` objects forming a hollow ring around this
            ``BNGReference``.
        bng_kdisc(k: int, return_relations: bool = False) -> list[BNGReference] |
            list[tuple[BNGReference, int, int]]:
            Returns a list of ``BNGReference`` objects forming a filled disc around this
            ``BNGReference``.
        bng_distance(bng_ref2: BNGReference, edge_to_edge: bool = False) -> float:
            Returns the euclidean distance between ``bng_ref2`` and this
            ``BNGReference``.
        bng_neighbours() -> list[BNGReference]: Returns a list of ``BNGReference``
            objects representing the four neighbouring grid squares sharing an edge
            with this ``BNGReference``.
        bng_is_neighbour(bng_ref2: BNGReference) -> bool: Tests whether ``bng_ref2`` is
            a neighbour of this ``BNGReference``.
        bng_dwithin(d:int | float) -> list[BNGReference]: Returns a list of
            ``BNGReference`` objects within a distance ``d`` from this ``BNGReference``.

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
        >>> bng_ref.bng_neighbours()
        [BNGReference(bng_ref_formatted=TQ 12 35, resolution_label=1km),
         BNGReference(bng_ref_formatted=TQ 13 34, resolution_label=1km),
         BNGReference(bng_ref_formatted=TQ 12 33, resolution_label=1km),
         BNGReference(bng_ref_formatted=TQ 11 34, resolution_label=1km)]
    """

    def __init__(self, bng_ref_string: str):
        """Initialises a ``BNGReference`` from a BNG reference string."""
        # Validate the BNG reference string
        if not _validate_bng_ref_string(bng_ref_string):
            raise BNGReferenceError(f"Invalid BNG reference string: '{bng_ref_string}'")

        # Remove all whitespace for internal storage
        self._bng_ref_compact = bng_ref_string.replace(" ", "")

    @property
    def bng_ref_compact(self) -> str:
        """The BNG reference string of this ``BNGReference`` with whitespace removed."""
        return self._bng_ref_compact

    @property
    def bng_ref_formatted(self) -> str:
        """The BNG reference string of this ``BNGReference`` in pretty format.

        Uses a single space between the prefix, easting, northing, and suffix to
        improve readability.
        """
        return _format_bng_ref_string(self._bng_ref_compact)

    @property
    def resolution_metres(self) -> int:
        """The resolution of this ``BNGReference`` in meters."""
        return _get_bng_resolution_metres(self._bng_ref_compact)

    @property
    def resolution_label(self) -> str:
        """The resolution of this ``BNGReference`` expressed as a string label.

        The resolution is returned in a human-readable format, such as '10km', '50km',
        '5km', etc.

        See Also:
            :data:`osbng.resolution.BNG_RESOLUTIONS` for mappings from metre-based
            integer resolution values to string label representations.
        """
        return _get_bng_resolution_label(self._bng_ref_compact)

    @property
    def __geo_interface__(self) -> dict[str, Union[str, dict]]:
        """A GeoJSON-like mapping of this ``BNGReference``.

        Implements the `__geo_interface__
        <https://gist.github.com/sgillies/2217756>`__ protocol. The returned data
        structure represents the :class:`~osbng.bng_reference.BNGReference` object as a
        GeoJSON-like Feature.
        """
        return {
            "type": "Feature",
            "properties": {
                "bng_ref": self.bng_ref_compact,
            },
            "geometry": mapping(self.bng_to_grid_geom()),
        }

    def __eq__(self, other: object):
        """Determines whether this ``BNGReference`` is equal to ``other``."""
        if isinstance(other, BNGReference):
            return self.bng_ref_compact == other.bng_ref_compact
        return False

    def __lt__(self, other: object):
        """Determines whether this ``BNGReference`` is ordered before ``other``.

        For two :class:`~osbng.bng_reference.BNGReference` objects, ordering is done in
        the following order:

        1. Rank by :attr:`~osbng.bng_reference.BNGReference.resolution_metres`, where
           higher resolutions are ordered first.
        2. Rank by :attr:`~osbng.bng_reference.BNGReference.bng_ref_compact`
           alphabetically.

        Example:
            >>> BNGReference("SU") < BNGReference("SU1234")
            True
            >>> BNGReference("SU") < BNGReference("TU")
            True
        """
        if isinstance(other, BNGReference):
            return (-self.resolution_metres, self.bng_ref_compact) < (
                -other.resolution_metres,
                other.bng_ref_compact,
            )
        return NotImplemented

    def __hash__(self):
        """Returns a hash value of this ``BNGReference``."""
        return hash(self.bng_ref_compact)

    def __repr__(self):
        """Returns the string representation of this ``BNGReference``."""
        return (
            f"BNGReference(bng_ref_formatted={self.bng_ref_formatted}, "
            f"resolution_label={self.resolution_label})"
        )

    def bng_to_xy(
        self, *, position: str = "lower-left"
    ) -> tuple[int | float, int | float]:
        """Returns easting and northing coordinates of this ``BNGReference``.

        An optional grid square ``position`` keyword argument can be specified to
        return the coordinates of a specific corner or the centre of the grid square.

        Keyword Args:
            position (str, optional): The grid square position expressed as a string.
                One of: 'lower-left', 'upper-left', 'upper-right', 'lower-right',
                'centre'.

        Returns:
            tuple[int | float, int | float]: Easting and northing coordinates as a
                tuple.

        Raises:
            ValueError: If invalid position provided.

        Example:
            >>> BNGReference("SU").bng_to_xy()
            (400000, 100000)
            >>> BNGReference("SU 3 1").bng_to_xy()
            (430000, 110000)
            >>> BNGReference("SU 3 1 NE").bng_to_xy("centre")
            (437500, 117500)
            >>> BNGReference("SU 37289 15541").bng_to_xy("centre")
            (437289.5, 115541.5)

        See Also:
            The equivalent :func:`osbng.indexing.bng_to_xy` function.
        """
        from osbng.indexing import bng_to_xy as _bng_to_xy

        return _bng_to_xy(self, position=position)

    def bng_to_bbox(self) -> tuple[int, int, int, int]:
        """Returns grid square bounding box coordinates of this ``BNGReference``.

        Returns:
            tuple[int, int, int, int]: The grid square bounding box coordinates as a
                tuple.

        Example:
            >>> BNGReference("SU").bng_to_bbox()
            (400000, 100000, 500000, 200000)
            >>> BNGReference("SU 3 1").bng_to_bbox()
            (430000, 110000, 440000, 120000)
            >>> BNGReference("SU 3 1 NE").bng_to_bbox()
            (435000, 115000, 440000, 120000)
            >>> BNGReference("SU 37289 15541").bng_to_bbox()
            (437289, 115541, 437290, 115542)

        See Also:
            The equivalent :func:`osbng.indexing.bng_to_bbox` function.
        """
        from osbng.indexing import bng_to_bbox as _bng_to_bbox

        return _bng_to_bbox(self)

    def bng_to_grid_geom(self) -> Polygon:
        """Returns a grid square as a ``Shapely Polygon`` of this ``BNGReference``.

        Returns:
            Polygon: Grid square as ``Shapely Polygon`` object.

        Example:
            >>> BNGReference("SU").bng_to_grid_geom().wkt
            'POLYGON ((500000 100000, 500000 200000, 400000 200000, 400000 100000,
                500000 100000))'
            >>> BNGReference("SU 3 1").bng_to_grid_geom().wkt
            'POLYGON ((440000 110000, 440000 120000, 430000 120000, 430000 110000,
                440000 110000))'
            >>> BNGReference("SU 3 1 NE").bng_to_grid_geom().wkt
            'POLYGON ((440000 115000, 440000 120000, 435000 120000, 435000 115000,
                440000 115000))'
            >>> BNGReference("SU 37289 15541").bng_to_grid_geom().wkt
            'POLYGON ((437290 115541, 437290 115542, 437289 115542, 437289 115541,
                437290 115541))'
        """
        from osbng.indexing import bng_to_grid_geom as _bng_to_grid_geom

        return _bng_to_grid_geom(self)

    def bng_to_children(
        self, *, resolution: int | str | None = None
    ) -> list["BNGReference"]:
        """Returns a list of child ``BNGReference`` objects of this ``BNGReference``.

        By default, the children of the :class:`~osbng.bng_reference.BNGReference`
        object is defined as the :class:`~osbng.bng_reference.BNGReference` objects in
        the next resolution down from the current ``BNGReference`` resolution. For
        example, 100km -> 50km.

        Notes:
            Any valid resolution can be provided as the child resolution, provided it
            is less than the resolution of the current
            :class:`~osbng.bng_reference.BNGReference` object.

        Keyword Args:
            resolution (int | str | None, optional): The resolution of the children
                :class:`~osbng.bng_reference.BNGReference` objects expressed either
                as a metre-based integer or as a string label. Defaults to None.

        Returns:
            list[BNGReference]: A list of BNGReference objects that are children of the
                current :class:`~osbng.bng_reference.BNGReference` object.

        Raises:
            BNGHierarchyError: If the resolution of the current
                :class:`~osbng.bng_reference.BNGReference` object is 1m.
            BNGHierarchyError: If the resolution is greater than or equal to the
                resolution of the current :class:`~osbng.bng_reference.BNGReference`
                object.
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

        See Also:
            The equivalent :func:`osbng.hierarchy.bng_to_children` function.
        """
        from osbng.hierarchy import bng_to_children as _bng_to_children

        return _bng_to_children(self, resolution=resolution)

    def bng_to_parent(self, *, resolution: int | str | None = None) -> "BNGReference":
        """Returns the ``BNGReference`` that is the parent of this ``BNGReference``.

        By default, the parent of the :class:`~osbng.bng_reference.BNGReference` object
        is defined as the :class:`~osbng.bng_reference.BNGReference` in the next BNG
        resolution up from the current :class:`~osbng.bng_reference.BNGReference`
        resolution. For example, 50km -> 100km.

        Notes:
            Any valid resolution can be provided as the parent resolution, provided it
            is greater than the resolution of the current
            :class:`~osbng.bng_reference.BNGReference` object.

        Keyword Args:
            resolution (int | str | None, optional): The resolution of the parent
                :class:`~osbng.bng_reference.BNGReference` objects expressed either as
                a metre-based integer or as a string label. Defaults to None.

        Returns:
            BNGReference: A :class:`~osbng.bng_reference.BNGReference` object that is
                the parent of the current :class:`~osbng.bng_reference.BNGReference`
                object.

        Raises:
            BNGHierarchyError: If the resolution of the current
                :class:`~osbng.bng_reference.BNGReference` object is 100km.
            BNGHierarchyError: If the resolution is less than or equal to the resolution
                of the current :class:`~osbng.bng_reference.BNGReference` object.
            BNGResolutionError: If an invalid resolution is provided.

        Examples:
            >>> BNGReference("SU 3 6 SW").bng_to_parent()
            BNGReference(bng_ref_formatted=SU 3 6, resolution_label=10km)
            >>> BNGReference("SU 342 567").bng_to_parent()
            BNGReference(bng_ref_formatted=SU 34 56 NW, resolution_label=500m)
            >>> BNGReference("SU 342 567").bng_to_parent(resolution=10000)
            BNGReference(bng_ref_formatted=SU 3 5, resolution_label=10km)

        See Also:
            The equivalent :func:`osbng.hierarchy.bng_to_parent` function.
        """
        from osbng.hierarchy import bng_to_parent as _bng_to_parent

        return _bng_to_parent(self, resolution=resolution)

    def bng_kring(
        self, k: int, *, return_relations: bool = False
    ) -> list["BNGReference"]:
        """Returns a hollow ring of BNGReference objects around this ``BNGReference``.

        Returns all :class:`~osbng.bng_reference.BNGReference` objects at a grid
        distance ``k``.

        Notes:
            Returned :class:`~osbng.bng_reference.BNGReference` objects are ordered
            North to South then West to East, therefore not in ring order.

        Args:
            k (int): Grid distance in units of grid squares.

        Keyword Args:
            return_relations (bool, optional): If True, returns a list of
                (BNGReference, dx, dy) tuples where dx, dy are integer offsets in grid
                units.  If False (default), returns a list of
                :class:`~osbng.bng_reference.BNGReference` objects.

        Returns:
            list[BNGReference]: All :class:`~osbng.bng_reference.BNGReference` objects
            representing squares in a square ring of radius k.

        Examples:
            >>> BNGReference("SU1234").bng_kring(1)
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
            >>> BNGReference("SU1234").bng_kring(1, return_relations=True)
            [
            (BNGReference(bng_ref_formatted=SU 11 35, resolution_label=1km), -1, 1),
            (BNGReference(bng_ref_formatted=SU 12 35, resolution_label=1km), 0, 1),
            (BNGReference(bng_ref_formatted=SU 13 35, resolution_label=1km), 1, 1),
            (BNGReference(bng_ref_formatted=SU 11 34, resolution_label=1km), -1, 0),
            (BNGReference(bng_ref_formatted=SU 13 34, resolution_label=1km), 1, 0),
            (BNGReference(bng_ref_formatted=SU 11 33, resolution_label=1km), -1, -1),
            (BNGReference(bng_ref_formatted=SU 12 33, resolution_label=1km), 0, -1),
            (BNGReference(bng_ref_formatted=SU 13 33, resolution_label=1km), 1, -1)
            ]
            >>> BNGReference("SU1234").bng_kring(3)
            [list of 24 BNGReference objects]

        See Also:
            The equivalent :func:`osbng.traversal.bng_kring` function.
        """
        from osbng.traversal import bng_kring as _bng_kring

        return _bng_kring(self, k, return_relations=return_relations)

    def bng_kdisc(
        self, k: int, *, return_relations: bool = False
    ) -> list["BNGReference"]:
        """Returns a filled disc of BNGReference objects around this ``BNGReference``.

        Returns all :class:`~osbng.bng_reference.BNGReference` objects up to a grid
        distance ``k``, including the given central
        :class:`~osbng.bng_reference.BNGReference` object.

        Notes:
            Returned :class:`~osbng.bng_reference.BNGReference` objects are ordered
            North to South then West to East.

        Args:
            k (int): Grid distance in units of grid squares.

        Keyword Args:
            return_relations (bool, optional): If True, returns a list of
                (BNGReference, dx, dy) tuples where dx, dy are integer offsets in grid
                units.  If False (default), returns a list of
                :class:`~osbng.bng_reference.BNGReference` objects.

        Returns:
            list[BNGReference]: All :class:`~osbng.bng_reference.BNGReference` objects
                representing grid squares in a square of radius ``k``.

        Examples:
            >>> BNGReference("SU1234").bng_kdisc(1)
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
            >>> BNGReference("SU1234").bng_kdisc(1, return_relations=True)
            [
            (BNGReference(bng_ref_formatted=SU 11 35, resolution_label=1km), -1, 1),
            (BNGReference(bng_ref_formatted=SU 12 35, resolution_label=1km), 0, 1),
            (BNGReference(bng_ref_formatted=SU 13 35, resolution_label=1km), 1, 1),
            (BNGReference(bng_ref_formatted=SU 11 34, resolution_label=1km), -1, 0),
            (BNGReference(bng_ref_formatted=SU 12 34, resolution_label=1km), 0, 0),
            (BNGReference(bng_ref_formatted=SU 13 34, resolution_label=1km), 1, 0),
            (BNGReference(bng_ref_formatted=SU 11 33, resolution_label=1km), -1, -1),
            (BNGReference(bng_ref_formatted=SU 12 33, resolution_label=1km), 0, -1),
            (BNGReference(bng_ref_formatted=SU 13 33, resolution_label=1km), 1, -1)
            ]
            >>> BNGReference("SU1234").bng_kdisc(3)
            [list of 49 BNGReference objects]

        See Also:
            The equivalent :func:`osbng.traversal.bng_kdisc` function.
        """
        from osbng.traversal import bng_kdisc as _bng_kdisc

        return _bng_kdisc(self, k, return_relations=return_relations)

    def bng_distance(
        self, bng_ref2: "BNGReference", *, edge_to_edge: bool = False
    ) -> float:
        """Returns the euclidean distance between bng_ref2 and this ``BNGReference``.

        When ``edge_to_edge`` is False, the distance is the centroid-to-centroid
        distance in metres.  When ``edge_to_edge`` is True, the distance is the
        shortest distance between any two parts of the grid squares.

        Notes:
            The other :class:`~osbng.bng_reference.BNGReference` object does not
            necessarily need to share a common resolution.  When ``edge_to_edge``
            = True and the two :class:`~osbng.bng_reference.BNGReference` objects have
            a parent-child relationship, the returned distance is 0.

        Args:
            bng_ref2 (BNGReference): A :class:`~osbng.bng_reference.BNGReference` object
                .

        Keyword Args:
            edge_to_edge (bool, optional): If False (default), distance will be
                centroid-to-centroid distance.  If True, distance will be the shortest
                distance between any point in the grid squares.

        Returns:
            float: The euclidean distance between the centroids of the two
            :class:`~osbng.bng_reference.BNGReference` objects.

        Raises:
            TypeError: If the ``bng_ref2`` argument is not a
            :class:`~osbng.bng_reference.BNGReference` object.

        Examples:
            >>> BNGReference("SE1433").bng_distance(BNGReference("SE1533"))
            1000.0
            >>> BNGReference("SE1433").bng_distance(
            ...     BNGReference("SE1533"), edge_to_edge=True
            ... )
            0.0
            >>> BNGReference("SE1433").bng_distance(BNGRerence("SE1631"))
            2828.42712474619
            >>> BNGReference("SE1433").bng_distance(BNGRerence("SE"))
            39147.158262126766
            >>> BNGReference("SE1433").bng_distance(BNGRerence("SENW"))
            42807.709586007986
            >>> BNGReference("SE").bng_distance(BNGRerence("OV"))
            141421.35623730952
            >>> BNGReference("SU").bng_distance(
            ...     BNGReference("SU2345"), edge_to_edge=True
            ... )
            0.0

        See Also:
            The equivalent :func:`osbng.traversal.bng_distance` function.
        """
        from osbng.traversal import bng_distance as _bng_distance

        return _bng_distance(self, bng_ref2, edge_to_edge=edge_to_edge)

    def bng_neighbours(self) -> list["BNGReference"]:
        """Returns the four BNGReference object neighbours to this BNGReference.

        The neighbours are defined as the grid squares immediately North, East, South
        and West of the input grid square sharing an edge with the input
        :class:`~osbng.bng_reference.BNGReference` object.

        Returns:
            list[BNGReference]: The grid squares immediately North, South, East and
            West of this :class:`~osbng.bng_reference.BNGReference` object.

        Examples:
            >>> BNGReference("SU1234").bng_neighbours()
            [BNGReference('SU1235'), BNGReference('SU1334'),
            BNGReference('SU1233'), BNGReference('SU1134')]

        See Also:
            The equivalent :func:`osbng.traversal.bng_neighbours` function.
        """
        from osbng.traversal import bng_neighbours as _bng_neighbours

        return _bng_neighbours(self)

    def bng_is_neighbour(self, bng_ref2: "BNGReference") -> bool:
        """Tests whether ``bng_ref2`` is a neighbour of this ``BNGReference``.

        Neighbours are defined as grid squares that share an edge with this
        :class:`~osbng.bng_reference.BNGReference` object.

        Args:
            bng_ref2 (BNGReference): A :class:`~osbng.bng_reference.BNGReference` object
            .

        Returns:
            bool: True if the two :class:`~osbng.bng_reference.BNGReference` objects are
            neighbours, otherwise False.

        Raises:
            TypeError: If the ``bng_ref2`` argument is not a
            :class:`~osbng.bng_reference.BNGReference` object.
            BNGNeighbourError: If the :class:`~osbng.bng_reference.BNGReference` object
            is not at the same resolution.

        Examples:
            >>> BNGReference("SE1921").bng_is_neighbour(BNGReference("SE1821"))
            True
            >>> BNGReference("SE1922").bng_is_neighbour(BNGReference("SE1821"))
            False
            >>> BNGReference("SU1234").bng_is_neighbour(BNGReference("SU1234"))
            False

        See Also:
            The equivalent :func:`osbng.traversal.bng_is_neighbour` function.
        """
        from osbng.traversal import bng_is_neighbour as _bng_is_neighbour

        return _bng_is_neighbour(self, bng_ref2)

    def bng_dwithin(self, d: int | float) -> list["BNGReference"]:
        """Returns all BNGReference objects within distance ``d`` of this BNGReference.

        All grid squares will be returned for which any part of its boundary is within
        distance ``d`` of any part of the :class:`~osbng.bng_reference.BNGReference`
        object's boundary.

        Args:
            d (int or float): The absolute distance ``d`` in metres.

        Returns:
            list[BNGReference]: All grid squares which have any part of their geometry
            within distance ``d`` of the current grid square

        Examples:
            >>> BNGReference("SU1234").bng_dwithin(1000)
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
            >>> BNGReference("SU1234").bng_dwithin(1001)
            [list of 21 BNGReference objects]

        See Also:
            The equivalent :func:`osbng.traversal.bng_dwithin` function.
        """
        from osbng.traversal import bng_dwithin as _bng_dwithin

        return _bng_dwithin(self, d)


def _validate_bngreferences(func: Callable) -> Callable:
    """Validates that a BNGReference object is passed as an arg or kwarg as expected."""

    @wraps(func)
    def wrapper(*args: Union[BNGReference], **kwargs: Union[BNGReference]) -> Callable:
        # Get the function's signature
        signature = inspect.signature(func)

        # Construct a bound form of the signature
        bound_signature = signature.bind(*args, **kwargs)

        # Iterate through each parameter in the signature
        for arg_name in signature.parameters.keys():
            # Identify the expected data type
            expected_type = signature.parameters.get(arg_name).annotation

            # Find the actual object provided to the argument
            arg_val = bound_signature.arguments.get(arg_name)

            # If a BNGReference is expected and the arg value is not a BNGReference,
            # raise an error
            if (expected_type == BNGReference) and not isinstance(
                arg_val, BNGReference
            ):
                raise TypeError(
                    f"A BNGReference object must be provided as the{arg_name} argument."
                )

        return func(*args, **kwargs)

    return wrapper
