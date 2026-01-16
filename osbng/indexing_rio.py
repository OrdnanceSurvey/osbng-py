"""Index rasters in Rasterio DatasetReader objects against the BNG index system.

Note:
    This module requires the 'Rasterio' (https://github.com/rasterio/rasterio)
    package to be installed.

    To install the required package, use:

        pip install osbng[rasterio]

"""

try:
    import rasterio as rio  # noqa: F401
except ImportError as e:
    raise ImportError(
        "The 'rasterio' package is required to use the 'osbng.indexing_rio' module. "
        "Install it with: pip install osbng[rasterio]"
    ) from e

from rasterio import DatasetReader
from shapely.geometry import box

from osbng.bng_reference import BNGReference
from osbng.errors import BNGExtentError, RasterIntersectionError


def _validate_within_extent(src: DatasetReader) -> None:
    """Validates that coordinates are within the bounds of the BNG index system extent.

    Args:
        src (DatasetReader): A rasterio dataset.

    Raises:
        BNGExtentError: If the raster bounds are outside the BNG index system extent.
    """
    rst_bbox = box(*src.bounds)
    bng_extent = box(0, 0, 700000, 1300000)
    if not rst_bbox.within(bng_extent):
        raise BNGExtentError(
            "The raster bounds are outside the BNG index system extent."
        )


def _validate_raster_bounds(src: DatasetReader, bng_ref: BNGReference) -> None:
    """Validates that the raster bounds intersect with the BNGReference bounds.

    Args:
        src (DatasetReader): A rasterio dataset.
        bng_ref (BNGReference): A BNGReference object.

    Raises:
        RasterIntersectionError: If the raster bounds do not intersect with the
        BNGReference bounds.
    """
    rst_bbox = box(*src.bounds)
    if not rst_bbox.intersects(bng_ref.bng_to_grid_geom()):
        raise RasterIntersectionError(
            "The raster bounds do not intersect with the BNGReference bounds."
        )
