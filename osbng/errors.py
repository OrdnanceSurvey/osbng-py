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
"""

from osbng.resolution import BNG_RESOLUTIONS


class BNGReferenceError(Exception):
    """Raised for invalid BNG reference strings."""

    pass


class BNGResolutionError(Exception):
    """Raised for unsupported BNG resolutions."""

    def __init__(self):
        """Initialise exception with a message listing supported resolutions."""
        # Extract the numeric and string resolutions from BNG_RESOLUTIONS
        # Create message listing supported resolutions
        message = (
            "Invalid BNG resolution provided. Supported resolutions are: \n"
            + f"Metres: {', '.join(map(str, BNG_RESOLUTIONS.keys()))}\n"
            + "Labels: "
            + f"{', '.join(value['label'] for value in BNG_RESOLUTIONS.values())}"
        )
        # Pass message to base class
        super().__init__(message)


class BNGHierarchyError(Exception):
    """Raised for invalid parent/child derivation."""

    pass


class BNGNeighbourError(Exception):
    """Raised for invalid neighbour relationships."""

    pass


class BNGExtentError(Exception):
    """Raised for coordinates outside the BNG index system extent.

    BNG extent defined as 0 <= easting < 700000 and 0 <= northing < 1300000
    """

    def __init__(self):
        """Initialise exception with a message listing the valid coordinate ranges."""
        # Create message listing the easting and northing coordinate ranges
        message = (
            "Coordinates outside of the BNG extent. "
            "Easting and northing values must be within: \n"
            "0 <= easting < 700000\n"
            "0 <= northing < 1300000"
        )
        # Pass message to base class
        super().__init__(message)


# Map exception strings to exception classes
_EXCEPTION_MAP = {
    "BNGReferenceError": BNGReferenceError,
    "BNGResolutionError": BNGResolutionError,
    "BNGHierarchyError": BNGHierarchyError,
    "BNGNeighbourError": BNGNeighbourError,
    "BNGExtentError": BNGExtentError,
}
