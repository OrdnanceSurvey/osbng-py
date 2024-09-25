"""
"""


import re

# Compile regular expression pattern for BNG reference
_pattern = re.compile(
    r"^[HJNOST][A-HJ-Z](\d{2}|\d{4}|\d{6}|\d{8}|\d{10})?(NE|SE|SW|NW)?$"
)

