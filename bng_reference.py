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
