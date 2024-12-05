"""Custom exceptions supporting interactions with the British National Grid (BNG).

These exceptions are intended to provide clear and specific error handling for scenarios where invalid inputs 
or operations are encountered.

Custom exceptions:
    - BNGReferenceError: Raised when an invalid BNG reference string is provided.
    - BNGResolutionError: Raised when an invalid BNG resolution is provided.
    - OutsideBNGExtentError: Raised when easting and northing coordinates fall outside of the defined extent of the BNG coordinate system.

Additional features:
    - EXCEPTION_MAP (dict): A dictionary that maps string representations of exception class names to their respective classes. This allows for 
    dynamic exception handling in a structured manner.
"""

from osbng.resolution import _RESOLUTION_TO_STRING


class BNGReferenceError(Exception):
    """Exception rasied for errors in BNG references."""

    pass


class BNGResolutionError(Exception):
    """Exception raised for unsupported BNG resolutions."""

    def __init__(self):
        # Extract the numeric and string resolutions from _resolution_to_string
        # Create message listing supported resolutions
        message = (
            "Invalid BNG resolution provided. Supported resolutions are: \n"
            f"Metres: {", ".join(map(str, _RESOLUTION_TO_STRING.keys()))}\n"
            f"Labels: {", ".join(value["label"] for value in _RESOLUTION_TO_STRING.values())}"
        )
        # Pass message to base class
        super().__init__(message)


class OutsideBNGExtentError(Exception):
    """Exception raised for easting and northing coordinates outside the BNG extent.

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
EXCEPTION_MAP = {
    "BNGReferenceError": BNGReferenceError,
    "BNGResolutionError": BNGResolutionError,
    "OutsideBNGExtentError": OutsideBNGExtentError,
}
