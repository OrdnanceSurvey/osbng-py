Indexing Rasterio
==================

.. automodule:: osbng.indexing_rio
   :members:
   :undoc-members:
   :show-inheritance:
   :exclude-members: BNGIndexedRaster

``BNGIndexedRaster``
--------------------

The :class:`~osbng.indexing_rio.BNGIndexedRaster` class represents a square BNG grid raster chip.

:class:`~osbng.indexing_rio.BNGIndexedRaster` objects are created when an input raster is decomposed at a
given BNG :doc:`resolution`.


.. autoclass:: BNGIndexedRaster
   :no-members:
   :no-inherited-members:
   :no-special-members:

Properties
~~~~~~~~~~

.. autosummary::
   :toctree: _autosummary

   BNGIndexedRaster.__repr__
   BNGIndexedRaster.bng_ref
   BNGIndexedRaster.is_core
   BNGIndexedRaster.transform
   BNGIndexedRaster.profile
   BNGIndexedRaster.count
   BNGIndexedRaster.height
   BNGIndexedRaster.width
   BNGIndexedRaster.nodata
   BNGIndexedRaster.dtypes
   BNGIndexedRaster.filepath_in
   BNGIndexedRaster.bounds_in
   BNGIndexedRaster.res

Methods
~~~~~~~

.. autosummary::
   :toctree: _autosummary

   BNGIndexedRaster.rst_read
   BNGIndexedRaster.rst_write
   BNGIndexedRaster.to_record
   BNGIndexedRaster.from_record

See Also
~~~~~~~~
.. autosummary::
   :toctree: _autosummary

   osbng.indexing_rio.rst_bounds_to_bng
   osbng.indexing_rio.rst_to_bng_intersection
   osbng.indexing_rio.rst_to_bng_intersection_iter