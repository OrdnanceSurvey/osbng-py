Indexing
========

.. automodule:: osbng.indexing
   :members:
   :undoc-members:
   :show-inheritance:
   :exclude-members: BNGIndexedGeometry

``BNGIndexedGeometry``
----------------------

The ``BNGIndexedGeometry`` class stores information about the relationship between an
input ``Shapely Geometry`` and the grid squares it intersects. This is particularly
useful for spatial indexing and analysis of geometries against the BNG index system.

The :class:`~osbng.indexing.BNGIndexedGeometry` class is instantiated as part of the
:func:`~osbng.indexing.geom_to_bng_intersection` indexing function that decomposes a
``Shapely Geometry`` into grid squares at a specified resolution.


.. autoclass:: BNGIndexedGeometry
   :no-members:
   :no-inherited-members:
   :no-special-members:

Properties
~~~~~~~~~~

.. autosummary::
   :toctree: _autosummary

   BNGIndexedGeometry.bng_ref
   BNGIndexedGeometry.is_core
   BNGIndexedGeometry.geom
   BNGIndexedGeometry.__repr__