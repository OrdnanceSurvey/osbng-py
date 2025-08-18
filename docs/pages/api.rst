Public API
==========

This page documents the public objects defined in ``osbng.__all__`` that are imported 
via:

.. code-block:: python

   from osbng import *

Included are the core functions for creating ``BNGReference`` objects from coordinates
or geometry objects, along with the main class used across the package. Also included 
are grid square data covering the BNG index system bounds as iterators at 100km, 50km, 
10km, 5km and 1km resolutions.

Additional functionality that works with ``BNGReference`` instances is documented in 
the respective module pages.

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   osbng.BNG_BOUNDS
   osbng.BNG_RESOLUTIONS
   osbng.BNGReference
   osbng.bng_grid_100km
   osbng.bng_grid_50km
   osbng.bng_grid_10km
   osbng.bng_grid_5km
   osbng.bng_grid_1km
   osbng.xy_to_bng
   osbng.bbox_to_bng
   osbng.bbox_to_bng_iterfeatures
   osbng.geom_to_bng
   osbng.geom_to_bng_intersection