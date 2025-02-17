"""Provides custom exceptions supporting interactions with the British National Grid (BNG) index system.

These exceptions are intended to provide clear and specific error handling for scenarios where invalid inputs 
or operations are encountered.

Custom exceptions:

    - BNGReferenceError: Raised when an invalid BNG reference string is provided.
    - BNGResolutionError: Raised when an invalid BNG resolution is provided.
    - BNGHierarchyError: Raised when an invalid parent/child derivation is attempted.
    - BNGExtentError: Raised when easting and northing coordinates fall outside of the defined extent of the BNG index system.

Additional features:

    - EXCEPTION_MAP (dict): A dictionary that maps string representations of exception class names to their respective classes. This allows for 
                            dynamic exception handling in a structured manner.
"""

from osbng.resolution import BNG_RESOLUTIONS


class BNGReferenceError(Exception):
    """Exception rasied for invalid BNG reference strings during BNGReference object creation."""

    pass


class BNGResolutionError(Exception):
    """Exception raised for unsupported BNG resolutions."""

    def __init__(self):
        # Extract the numeric and string resolutions from BNG_RESOLUTIONS
        # Create message listing supported resolutions
        message = (
            "Invalid BNG resolution provided. Supported resolutions are: \n"
            f"Metres: {", ".join(map(str, BNG_RESOLUTIONS.keys()))}\n"
            f"Labels: {", ".join(value["label"] for value in BNG_RESOLUTIONS.values())}"
        )
        # Pass message to base class
        super().__init__(message)


class BNGHierarchyError(Exception):
    """Exception raised for invalid parent/child derivation"""

    pass


class BNGNeighbourError(Exception):
    """Exception raised for invalid BNG Resolution objects, either they are not the same grid resolution or are identical objects."""

    pass


class BNGExtentError(Exception):
    """Exception raised for easting and northing coordinates outside the BNG index system extent.

    BNG extent defined as 0 <= easting < 700000 and 0 <= northing < 1300000"""

    def __init__(self):
        # Create message listing the easting and northing coordinate ranges
        message = (
            "Coordinates outside of the BNG extent. Easting and northing values must be within: \n"
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
