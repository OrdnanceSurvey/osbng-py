Public API
==========

This page documents the public objects defined in ``osbng.__all__`` that are imported 
via:

.. code-block:: python

   from osbng import *

Included are the core functions for creating :class:`~osbng.bng_reference.BNGReference` objects from 
coordinates or Shapely_  geometry objects, along with the main class used across the 
package. Also included are grid square data covering the BNG index system bounds as 
iterators at 100km, 50km, 10km, 5km and 1km resolutions.

.. _Shapely:
   https://github.com/shapely/shapely

Additional functionality that works with :class:`~osbng.bng_reference.BNGReference` instances is 
documented in the respective module pages and can be imported from ``osbng`` modules 
directly. For example:

.. code-block:: python

   from osbng.bng_reference import BNGReference
   from osbng.hierarchy import bng_to_children
   from osbng.indexing import bng_to_bbox
   from osbng.indexing_gpd import gdf_to_bng_intersection_explode
   from osbng.traversal import bng_kdisc

Public API reference. This links the canonical module documentation for each object:

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   osbng.grids.BNG_BOUNDS
   osbng.resolution.BNG_RESOLUTIONS
   osbng.indexing.PREFIXES
   osbng.indexing.SUFFIXES
   osbng.bng_reference.BNGReference
   osbng.grids.bng_grid_100km
   osbng.grids.bng_grid_50km
   osbng.grids.bng_grid_10km
   osbng.grids.bng_grid_5km
   osbng.grids.bng_grid_1km
   osbng.indexing.xy_to_bng
   osbng.indexing.bbox_to_bng
   osbng.grids.bbox_to_bng_iterfeatures
   osbng.indexing.geom_to_bng
   osbng.indexing.geom_to_bng_intersection