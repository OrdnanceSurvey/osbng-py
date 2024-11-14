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
