"""Defines the supported resolutions for the British National Grid (BNG) index system.

Supported BNG resolutions are: 

- 100km
- 50km
- 10km
- 5km
- 1km
- 500m
- 100m
- 50m
- 10m
- 5m
- 1m

Relates metre-based BNG resolutions, expressed as integer values, to their respective string label representations. 
These mappings are used to indicate different resolution precision levels in BNG references and serve as the basis for validating 
and normalising resolutions within the system.

The integer values represent spatial resolutions in metres, while the string labels provide a human-readable descriptor
for each resolution level. For example, the numeric resolution 1000 is mapped to the label '1km'.

The resolution mappings also include a flag indicating whether a given resolution represents an (intermediate) quadtree resolution.
Quadtree resolutions are used to subdivide BNG grid squares at (standard) powers of ten resolutions into four equal quadrants, 
providing additional levels of precision for spatial indexing.

These resolution mappings establish the allowable values that functions and objects referencing the system can accept and process.
"""

__all__ = ["BNG_RESOLUTIONS"]

# Supported BNG resolutions
# Mappings from metre-based integer values to string label representations
# Quadtree flag indicates whether resolution represents an intermediate quadtree level
BNG_RESOLUTIONS = {
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
