"""This module defines the supported British National Grid (BNG) resolution mappings.

It relates metre-based integer values to their respective string label representations. These mappings
are used to indicate differe precision levels in BNG references and serve as the basis for validating 
and normalising resolutions within the system.

The integer values represent spatial resolutions in metres, while the string labels provide a human-readable descriptor
for each resolution level. For example, the numeric resolution 1000 is mapped to the label '1km'.

These resolution mappings establish the allowable values that functions and objects referencing the system can accept and process."""

# BNG resolution mappings from metre-based integer values to string label representations
_RESOLUTION_TO_STRING = {
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
