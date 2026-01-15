# Changelog

All notable changes to this project will be documented in this file.

## [0.5.0] - 2026-01-15

### Added

- First public release of `osbng`, a Python package supporting geospatial grid indexing and interaction with Ordnance Survey's British National Grid (BNG) index system.
- `BNGReference`:
  - Core class providing a structured representation for BNG grid references.
  - Parsing and validation of BNG grid references from strings.
  - Objects can be compared, ordered, and are hashable.
  - GeoJSON-like mapping for grid squares via `__geo_interface__`.
- Indexing:
  - Encoding easting and northing coordinates into `BNGReference` objects at a specified resolution.
  - Decoding `BNGReference` objects back into coordinates, bounding boxes and grid squares as `Shapely` geometries.
  - Indexing bounding boxes and `Shapely` geometries into grid squares at a specified resolution.
  - Optional indexing of geometries in a `GeoPandas GeoDataFrame` into grid squares at a specified resolution.
- Hierarchy:
  - Returning parents and children of `BNGReference` objects at specified resolutions.
- Traversal:
  - Generation of k-discs and k-rings around a given grid square.
  - Identification of neighbouring grid squares and checking adjacency.
  - Calculating the distance between grid square centroids.
  - Retrieving all grid squares within a specified absolute distance.
- Grids:
  - Grid square data covering the BNG index system bounds provided as iterators at 100km, 50km, 10km, 5km and 1km resolutions.
- Example Jupyter notebooks demonstrating typical package usage.
- Sphinx-based documentation published on Read the Docs.

### Notes

- The project is currently marked as **Beta**.
- While the core concepts and interfaces are expected to remain consistent, breaking change may occur in future `0.x` releases prior to `1.0.0`.
