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

from osbng.errors import BNGExtentError


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
