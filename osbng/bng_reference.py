"""
"""

import re

# Compile regular expression pattern for BNG reference
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
