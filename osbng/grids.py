"""Provides functionality to generate British National Grid (BNG) grid square data within specified bounds.

Uses a GeoJSON-like mapping for grid squares implementing the __geo_interface__ protocol (https://gist.github.com/sgillies/2217756).

Use of this protocol enables integration with geospatial data processing libraries and tools.
"""

# BNG index system bounds
BNG_BOUNDS = (0, 0, 700000, 1300000)