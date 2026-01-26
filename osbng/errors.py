"""Custom exceptions for the ``osbng`` package.

These exceptions are intended to provide clear and specific error handling for
scenarios where invalid inputs or operations are encountered.

Custom exceptions:

- **BNGExtentError**: Raised when easting and northing coordinates fall outside of the
  BNG index system extent.
- **BNGHierarchyError**: Raised when an invalid parent or child derivation is attempted.
- **BNGNeighbourError**: Raised when an invalid neighbour relationship is encountered.
- **BNGReferenceError**: Raised when an invalid BNG reference string is provided.
- **BNGResolutionError**: Raised when an invalid BNG resolution is provided.
- **RasterCRSError**: Raised when a raster is not in the British National Grid CRS
 (EPSG:27700).
- **RasterIntersectionError**: Raised when a raster does not intersect with the
 BNGReference bounds.
- **RasterResError**: Raised when the raster res does not tesselate within the BNG grid
 square.
"""

from osbng.resolution import BNG_RESOLUTIONS


class BNGReferenceError(Exception):
    """Raised for invalid BNG reference strings."""

    pass


class BNGResolutionError(Exception):
    """Raised for unsupported BNG resolutions.

    Args:
        message (str | None): Optional additional message to include.
    """

    def __init__(self, message: str | None = None):
        """Initialise exception with a message listing supported resolutions."""
        # Extract the numeric and string resolutions from BNG_RESOLUTIONS
        # Create message listing supported resolutions
        _message = (
            "Invalid BNG resolution provided. Supported resolutions are: \n"
            + f"Metres: {', '.join(map(str, BNG_RESOLUTIONS.keys()))}\n"
            + "Labels: "
            + f"{', '.join(value['label'] for value in BNG_RESOLUTIONS.values())}"
        )
        if message:
            _message = message + "\n" + _message
        # Pass message to base class
        super().__init__(_message)


class BNGHierarchyError(Exception):
    """Raised for invalid parent/child derivation."""

    pass


class BNGNeighbourError(Exception):
    """Raised for invalid neighbour relationships."""

    pass


class BNGExtentError(Exception):
    """Raised for coordinates outside the BNG index system extent.

    BNG extent defined as 0 <= easting < 700000 and 0 <= northing < 1300000

    Args:
        message (str | None): Optional additional message to include.
    """

    def __init__(self, message: str | None = None):
        """Initialise exception with a message listing the valid coordinate ranges."""
        # Create message listing the easting and northing coordinate ranges
        _message = (
            "Coordinates outside of the BNG extent. "
            "Easting and northing values must be within: \n"
            "0 <= easting < 700000\n"
            "0 <= northing < 1300000"
        )
        if message:
            _message = message + "\n" + _message
        # Pass message to base class
        super().__init__(_message)


class RasterIntersectionError(Exception):
    """Raised when a raster does not intersect with the BNGReference bounds."""

    pass


class RasterResError(Exception):
    """Raised when the raster res does not tesselate within the BNG grid square."""

    pass


class RasterCRSError(Exception):
    """Raised when a raster is not in the British National Grid CRS (EPSG:27700)."""

    pass


# Map exception strings to exception classes
_EXCEPTION_MAP = {
    "BNGReferenceError": BNGReferenceError,
    "BNGResolutionError": BNGResolutionError,
    "BNGHierarchyError": BNGHierarchyError,
    "BNGNeighbourError": BNGNeighbourError,
    "BNGExtentError": BNGExtentError,
    "RasterIntersectionError": RasterIntersectionError,
    "RasterResError": RasterResError,
    "RasterCRSError": RasterCRSError,
}
