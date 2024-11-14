"""Custom exceptions supporting interactions with the British National Grid (BNG)."""

from osbng.resolution import _resolution_to_string


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
            f"Metres: {", ".join(map(str, _resolution_to_string.keys()))}\n"
            f"Labels: {", ".join(_resolution_to_string.values())}"
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
