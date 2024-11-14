"""
"""

from osbng.errors import BNGResolutionError
from osbng.resolution import _resolution_to_string


def _validate_and_normalise_bng_resolution(resolution: int | str):
    """Validates and normalises a BNG resolution to its metre-based integer value.

    Args:
        resolution (int or str): The Resolution, either as a metre-based integer or string label.

    Returns:
        int: The numeric metre-based resolution.

    Raises:
        BNGResolutionError: If an invalid resolution is provided.

    Example:
        >>> _validate_and_normalise_bng_resolution(1000)
        1000
        >>> _validate_and_normalise_bng_resolution("1km")
        1000
    """

    # If resolution is an integer, check if it's a valid metre-based resolution
    if isinstance(resolution, int):
        if resolution not in _resolution_to_string.keys():
            raise BNGResolutionError()
        return resolution

    # If resolution is a string, check if it's a valid resolution label
    elif isinstance(resolution, str):
        if resolution not in _resolution_to_string.values():
            raise BNGResolutionError()
        # Get the corresponding metre-based resolution
        return next(
            res for res, label in _resolution_to_string.items() if label == resolution
        )

    # If resolution is neither an integer nor a string, raise BNGResolutionError
    else:
        raise BNGResolutionError()
