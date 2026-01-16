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
from osbng.errors import (
    BNGExtentError,
    BNGResolutionError,
    RasterCRSError,
    RasterIntersectionError,
    RasterResError,
)


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


def _evaluate_resolution_compatibility(rst_res: tuple, bng_resolution: int) -> None:
    """Evaluates if the raster resolution is compatible with the target BNG resolution.

    Notes:
        - Raster pixels must be square (equal x and y resolution).
        - The BNG resolution must be at least twice the raster resolution.
        - If the raster resolution is not a factor of the BNG resolution, the input
        raster must be resampled/transformed prior to indexing.

    Args:
        rst_res (tuple): The raster resolution as a (xres, yres) tuple.
        bng_resolution (int): The target BNG resolution in metres.

    Raises:
        RasterResError: If the raster pixels are not square (equal x and y resolution),
         or if the raster resolution is not a factor of the BNG resolution.
        BNGResolutionError: If the raster resolution is not compatible with the target
         BNG resolution.
    """
    if rst_res[0] != rst_res[1]:
        raise RasterResError(
            "Input raster must have square pixels (equal x and y resolution)."
        )

    # require that the BNG resolution is at least twice the raster resolution
    if bng_resolution < 2 * rst_res[0]:
        raise BNGResolutionError(
            f"Input raster resolution {rst_res[0]}m is too coarse for target BNG "
            f"resolution {bng_resolution}m. BNG resolution must be at least twice "
            "the raster resolution."
        )

    # check if raster resolution is a factor of BNG resolution
    if bng_resolution % rst_res[0] != 0:
        raise RasterResError(
            f"Input raster resolution {rst_res[0]} m is not a factor of target BNG "
            f"resolution {bng_resolution} m. Please resample/transform the input "
            "raster prior to indexing."
        )


def _validate_crs(src: DatasetReader) -> None:
    """Validates that the input raster is in the British National Grid CRS (EPSG:27700).

    Args:
        src (DatasetReader): An open rasterio dataset.

    Raises:
        RasterCRSError: If the raster's CRS is not EPSG:27700.
    """
    if src.crs.to_epsg() != 27700:
        raise RasterCRSError(
            "Input raster must be in British National Grid CRS (EPSG:27700). "
            f"CRS found: {src.crs}"
        )
