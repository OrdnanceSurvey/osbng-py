BNG Reference
=============

.. currentmodule:: osbng.bng_reference

.. automodule:: osbng.bng_reference
   :no-members:
   :no-inherited-members:
   :no-special-members:

``BNGReference``
----------------

The ``BNGReference`` class supports the conversion of a BNG reference string into a
:class:`~osbng.bng_reference.BNGReference` object, ensuring type consistency across the
package. All functions accepting or returning BNG references enforce the use of this
class. 

These functions are available both as instance methods of the class and as standalone 
functions, providing users with the flexibility to either:

- Create a :class:`~osbng.bng_reference.BNGReference` object and pass it to a
  function.
- Create a :class:`~osbng.bng_reference.BNGReference` object and use one of its
  instance methods.


.. autoclass:: BNGReference
   :no-members:
   :no-inherited-members:
   :no-special-members:

Properties
~~~~~~~~~~

.. autosummary::
   :toctree: _autosummary

   BNGReference.bng_ref_compact
   BNGReference.bng_ref_formatted
   BNGReference.resolution_metres
   BNGReference.resolution_label
   BNGReference.__geo_interface__

Methods
~~~~~~~

.. autosummary::
   :toctree: _autosummary

   BNGReference.bng_to_xy
   BNGReference.bng_to_bbox
   BNGReference.bng_to_grid_geom
   BNGReference.bng_to_children
   BNGReference.bng_to_parent
   BNGReference.bng_kring
   BNGReference.bng_kdisc
   BNGReference.bng_distance
   BNGReference.bng_neighbours
   BNGReference.bng_is_neighbour
   BNGReference.bng_dwithin