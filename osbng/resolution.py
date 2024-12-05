"""Defines the supported British National Grid (BNG) resolution mappings.

Relates metre-based integer values to their respective string label representations. These mappings
are used to indicate different precision levels in BNG references and serve as the basis for validating 
and normalising resolutions within the system.

The integer values represent spatial resolutions in metres, while the string labels provide a human-readable descriptor
for each resolution level. For example, the numeric resolution 1000 is mapped to the label '1km'.

The resolution mappings also include a flag indicating whether a given resolution represents an (intermediate) quadtree resolution.
Quadtree resolutions are used to subdivide BNG grid squares at (standard) powers of ten resolutions into four equal quadrants, providing additional levels of precision for spatial indexing.

These resolution mappings establish the allowable values that functions and objects referencing the system can accept and process.
"""

# BNG resolution mappings from metre-based integer values to string label representations
_RESOLUTION_TO_STRING = {
    100000: {"label": "100km", "quadtree": False},
    50000: {"label": "50km", "quadtree": True},
    10000: {"label": "10km", "quadtree": False},
    5000: {"label": "5km", "quadtree": True},
    1000: {"label": "1km", "quadtree": False},
    500: {"label": "500m", "quadtree": True},
    100: {"label": "100m", "quadtree": False},
    50: {"label": "50m", "quadtree": True},
    10: {"label": "10m", "quadtree": False},
    5: {"label": "5m", "quadtree": True},
    1: {"label": "1m", "quadtree": False},
}
