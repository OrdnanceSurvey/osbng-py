# OSBNG

A Python library for Ordnance Survey's British National Grid index system. This library provides tools for working with the British National Grid, a rectangular Cartesian grid system used to identify and index locations across Great Britain into grid squares at various resolutions.

## Overview

The OSBNG Python package provides a programmatic interface to the British National Grid (BNG), supporting efficient grid-based indexing and spatial analysis. This enables applications such as statistical aggregation, data visualization, and data interoperability using BNG grid references. Designed for developers working with geospatial data in the context of Great Britain, the library offers tools to simplify working with the BNG, facilitating both technical integration into geospatial workflows and practical exploration of the index system's structure.

The package supports the 'standard' BNG metre-based resolutions, which represent powers of ten from 1m to 100km (1m, 10m, 100m, 1km, 10km, 100km). It also supports the 'intermediate' quadtree resolutions (5m, 50m, 500m, 5km, 50km), identified by an ordinal (SW, NW, SE, NE) BNG reference direction suffix.

## Installation

Install OSBNG from PyPI using `pip` or conda-forge using `conda`:

``` shell
$ pip install osbng
```

``` shell
$ conda install -c conda-forge osbng
```

## Usage

The OSBNG package is structured into modules supporting different interactions with the BNG index system (e.g. indexing, hierarchy, traversal). A high-level summary of each module is provided below:

### BNG Reference

OSBNG implements a custom BNG reference object, `BNGReference`. All BNG references are instances of this class, enforcing type consistency across the package.

### Indexing

Provides the ability to index and work with coordinates and geometries against the BNG system. This includes:

* Encoding easting and northing coordinates into BNG reference objects at a specified resolution.
* Decoding BNG reference objects back into coordinates and grid squares as [`Shapely`](https://github.com/shapely/shapely) geometries.
* Indexing Shapely geometries into grid squares at a specified resolution for spatial analysis.

The following examples demonstrate the construction of a BNG Reference object from a reference string and from easting northing coordinates:

``` python
>>> from osbng.bng_reference import BNGReference
>>> bng = BNGReference(bng_ref_string="ST57SE")
>>> bng.bng_ref_formatted
'ST 5 7 SE'
>>> bng.resolution_metres
5000
```

``` python
>>> from osbng.indexing import xy_to_bng
>>> bng = xy_to_bng(easting=356976, northing=171421, resolution=5000)
>>> bng.bng_ref_formatted
'ST 5 7 SE'
>>> bng.resolution_label
'5km'
>>> bng.bng_to_xy(position="lower-left")
(355000, 170000)
```

## License

The OSBNG package is licensed under the terms of the MIT License.
