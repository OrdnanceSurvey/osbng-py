"""Index rasters in ``Rasterio`` ``DatasetReader`` objects against the BNG index system.

Note:
    This module requires the `Rasterio <https://github.com/rasterio/rasterio>`__
    package to be installed.

    To install the required package, use:

        pip install osbng[rasterio]

"""

try:
    import rasterio as rio
except ImportError as e:
    raise ImportError(
        "The 'rasterio' package is required to use the 'osbng.indexing_rio' module. "
        "Install it with: pip install osbng[rasterio]"
    ) from e

import glob
import os
from typing import Iterator, Self

import numpy as np
from rasterio import DatasetReader
from rasterio.coords import BoundingBox
from rasterio.errors import RasterioIOError
from rasterio.profiles import Profile
from rasterio.transform import Affine, guard_transform
from rasterio.windows import Window, from_bounds
from rasterio.windows import transform as window_transform
from shapely.geometry import box

from osbng.bng_reference import BNGReference
from osbng.errors import (
    BNGExtentError,
    BNGResolutionError,
    RasterCRSError,
    RasterIntersectionError,
    RasterResError,
)
from osbng.indexing import bbox_to_bng

__all__ = [
    "BNGIndexedRaster",
    "rst_bounds_to_bng",
    "rst_to_bng_intersection",
    "rst_to_bng_intersection_iter",
]


def _validate_within_extent(src: DatasetReader) -> None:
    """Validates that coordinates are within the bounds of the BNG index system extent.

    Args:
        src (DatasetReader): A Rasterio dataset.

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
        src (DatasetReader): A Rasterio dataset.
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
        src (DatasetReader): An open Rasterio dataset.

    Raises:
        RasterCRSError: If the raster's CRS is not EPSG:27700.
    """
    if src.crs.to_epsg() != 27700:
        raise RasterCRSError(
            "Input raster must be in British National Grid CRS (EPSG:27700). "
            f"CRS found: {src.crs}"
        )


class BNGIndexedRaster:
    """Represents a square BNG grid raster chip.

      ``BNGIndexedRaster`` objects are created when an input raster is decomposed at a
        given BNG resolution.

    Attributes:
        bng_ref (BNGReference): The :class:`~osbng.bng_reference.BNGReference` object
        for this raster chip.
        is_core (bool): A boolean flag indicating whether this square BNG grid raster
          chip is entirely contained by the input raster bounds.
        transform (rio.transform.Affine): The affine transformation matrix for this
          raster chip.
        profile (rio.profiles.Profile): The Rasterio profile for this raster chip.
        count (int): The number of bands in this raster chip.
        height (int): The height of this raster chip in pixels.
        width (int): The width of this raster chip in pixels.
        nodata (int): The nodata value for this raster chip.
        dtypes (list): The data types of this raster chip's bands.
        filepath_in (str): The file path to the input raster.
        bounds_in (rio.coords.BoundingBox): The bounding box of the input raster.
        res (tuple): The pixel resolution of this raster chip as a (xres, yres) tuple.

    Methods:
        rst_read(**kwargs) -> np.ndarray:
            Reads this raster chip's data into memory.
        rst_write(filepath_out: str, *, read_kw: dict|None=None, **kwargs) -> None:
            Writes this raster chip to a file.
        to_record() -> dict:
            Serialises this ``BNGIndexedRaster`` object to a dictionary record.
        from_record(record: dict) -> Self:
            Deserialises a ``BNGIndexedRaster`` object from a dictionary record.

    See Also:
        rst_bounds_to_bng: Converts raster bounds to ``BNGReference`` list.
        rst_to_bng_intersection: Converts a raster to a ``BNGIndexedRaster`` list.
        rst_to_bng_intersection_iter: Yields ``BNGIndexedRaster`` objects for
        rasters in a directory.
        BNGIndexedGeometry: Vector equivalent of this class.
    """

    def __init__(self, src: DatasetReader | str, bng_ref: BNGReference):
        """Initialises a ``BNGIndexedRaster`` object.

        Args:
            src (rasterio.io.DatasetReader | str): An open Rasterio dataset or a file
              path to a raster.
            bng_ref (BNGReference): A :class:`~osbng.bng_reference.BNGReference` object.

        Raises:
            RasterCRSError: If the raster is not in the British National Grid CRS
              (EPSG:27700).
            BNGExtentError: If the raster bounds are outside the BNG index system
              extent.
            RasterIntersectionError: If the raster bounds do not intersect with the
              ``BNGReference`` bounds.
            RasterResError: If the raster pixels are not square (equal x and y
              res), or if the raster resolution is not a factor of the BNG resolution.
            BNGResolutionError: If the raster resolution is not compatible with the
              target BNG resolution.
            :class:`~rasterio.errors.RasterioIOError`: If ``src`` is neither a Rasterio
              ``DatasetReader`` nor a valid file path string.
        """
        if isinstance(src, DatasetReader):
            self._src = src
        else:
            try:
                self._src = rio.open(src)
            except Exception:
                raise RasterioIOError(
                    "src must be a Rasterio ``DatasetReader`` or a file path string to"
                    " a valid raster file."
                )
        self._profile = self._src.profile.copy()  # store original profile while open
        self._in_res = self._src.res
        self._bng_ref = bng_ref
        _validate_crs(self._src)
        _validate_within_extent(self._src)
        _validate_raster_bounds(self._src, bng_ref)
        _evaluate_resolution_compatibility(self._src.res, bng_ref.resolution_metres)

        self._src.close()  # close the dataset to avoid open file handles

    def __repr__(self) -> str:
        """String representation of this ``BNGIndexedRaster`` object."""
        return (
            f"BNGIndexedRaster(src='{self.filepath_in}', "
            f"bng_ref=BNGReference({self.bng_ref.bng_ref_compact}))"
        )

    @property
    def _window(self) -> Window:
        """The Rasterio window object for this raster chip."""
        return from_bounds(*self.bng_ref.bng_to_bbox(), self._src.transform)

    @property
    def bng_ref(self) -> BNGReference:
        """The ``BNGReference`` object for this raster chip."""
        return self._bng_ref

    @property
    def transform(self) -> Affine:
        """The affine transformation matrix for this raster chip."""
        return window_transform(self._window, guard_transform(self._src.transform))

    @property
    def profile(self) -> Profile:
        """The Rasterio profile for this raster chip."""
        profile = self._profile
        profile.update(
            {"height": self.height, "width": self.width, "transform": self.transform}
        )
        return profile

    @property
    def count(self) -> int:
        """The number of bands in this raster chip."""
        return self._src.count

    @property
    def height(self) -> int:
        """The height of this raster chip in pixels."""
        return round(self._window.height)

    @property
    def width(self) -> int:
        """The width of this raster chip in pixels."""
        return round(self._window.width)

    @property
    def nodata(self) -> int:
        """The nodata value for this raster chip."""
        return self._src.nodata

    @property
    def dtypes(self) -> list:
        """The data types of this raster chip's bands."""
        return self._src.dtypes

    @property
    def filepath_in(self) -> str:
        """The file path to the input raster."""
        return self._src.name

    @property
    def bounds_in(self) -> BoundingBox:
        """The bounding box of the input raster."""
        return self._src.bounds

    @property
    def is_core(self) -> bool:
        """Whether this BNG raster chip is entirely within the input raster bounds.

        Note that this does not preclude this raster chip from having nodata values.
        """
        rst_bbox = box(*self.bounds_in)
        return rst_bbox.contains(self.bng_ref.bng_to_grid_geom())

    @property
    def res(self) -> tuple:
        """The pixel resolution of this raster chip as a (xres, yres) tuple."""
        return self._src.res

    def rst_read(self, **kwargs) -> np.ndarray:
        """Reads this raster chip data into memory.

        Keyword Args:
            **kwargs: Additional keyword arguments to pass to Rasterio's read function.

        Returns:
            np.ndarray: A NumPy array containing the raster chip data.

        """
        with rio.open(self.filepath_in) as dataset:
            rst = dataset.read(window=self._window, boundless=True, **kwargs)

        return rst

    def rst_write(
        self,
        filepath_out: str,
        *,
        verbose: bool = False,
        read_kw: dict | None = None,
        **kwargs,
    ) -> None:
        """Writes this raster chip to a file.

        Args:
            filepath_out (str): The file path to write this raster chip to.

        Keyword Args:
            verbose (bool): If True, prints a message indicating the output file path.
              Defaults to False.
            read_kw (dict|None): Additional keyword arguments to pass to Rasterio's read
              function.
            **kwargs: Additional keyword arguments to pass to Rasterio's write function.

        """
        read_kwargs = read_kw if read_kw else {}

        with rio.open(self.filepath_in) as dataset:
            rst = dataset.read(window=self._window, boundless=True, **read_kwargs)

            with rio.open(filepath_out, "w", **self.profile) as dst:
                dst.write(rst, **kwargs)

        if verbose:
            print(f"Raster chip written to {filepath_out}")

    def to_record(self) -> dict:
        """Serialises this ``BNGIndexedRaster`` object to a record.

        Returns:
            dict: A dictionary representation of this
            ``BNGIndexedRaster`` object.

        See Also:
            from_record: Deserialises a ``BNGIndexedRaster`` object from a record.
        """
        record = {
            "bng_ref": self.bng_ref.bng_ref_compact,
            "is_core": self.is_core,
            "transform": {
                "a": self.transform.a,
                "b": self.transform.b,
                "c": self.transform.c,
                "d": self.transform.d,
                "e": self.transform.e,
                "f": self.transform.f,
            },
            "count": self.count,
            "height": self.height,
            "width": self.width,
            "nodata": self.nodata,
            "dtypes": {band: dtype for band, dtype in enumerate(self.dtypes, start=1)},
            "filepath_in": self.filepath_in,
            "bounds_in": {
                "xmin": self.bounds_in.left,
                "ymin": self.bounds_in.bottom,
                "xmax": self.bounds_in.right,
                "ymax": self.bounds_in.top,
            },
            "res": self.res[0],
        }
        return record

    @classmethod
    def from_record(cls, record: dict) -> Self:
        """Deserialises a ``BNGIndexedRaster`` object from a record.

        Args:
            record (dict): A dictionary representation of a
            ``BNGIndexedRaster`` object.

        Returns:
            BNGIndexedRaster: The deserialised ``BNGIndexedRaster`` object.

        See Also:
            to_record: Serialises this ``BNGIndexedRaster`` object to a record.
        """
        bng_ref = BNGReference(record["bng_ref"])
        return cls(src=record["filepath_in"], bng_ref=bng_ref)


def rst_bounds_to_bng(
    src: DatasetReader | str, resolution: int | str
) -> list[BNGReference]:
    """Returns a ``BNGReference`` list given the BNG resolution and the raster's bounds.

    A :class:`~osbng.bng_reference.BNGReference` object is created for each BNG grid
    square that intersects with the raster bounds at the specified resolution.

    Args:
        src (rasterio.io.DatasetReader | str): An open Rasterio dataset or a file path
          to a raster.
        resolution (int | str): The BNG resolution expressed either as a metre-based
            integer or as a string label.

    Returns:
        list[BNGReference]: A list of ``BNGReference`` objects covering the raster
        bounds.

    Raises:
        RasterCRSError: If the raster is not in the British National Grid CRS
          (EPSG:27700).
        BNGExtentError: If the raster bounds are outside the BNG index system
          extent.
        BNGResolutionError: If an invalid resolution is provided.
        :class:`~rasterio.errors.RasterioIOError`: If ``src`` is neither a Rasterio
          ``DatasetReader`` nor a valid file path string.
    """
    if isinstance(src, DatasetReader):
        _validate_crs(src)
        _validate_within_extent(src)
        return bbox_to_bng(*src.bounds, resolution)
    else:
        try:
            with rio.open(src) as dataset:
                _validate_crs(dataset)
                _validate_within_extent(dataset)
                return bbox_to_bng(*dataset.bounds, resolution)
        except Exception:
            raise RasterioIOError(
                "src must be a Rasterio ``DatasetReader`` or a file path string to a "
                "valid raster file."
            )


def rst_to_bng_intersection(
    src: DatasetReader | str,
    resolution: int | str,
) -> list[BNGIndexedRaster]:
    """Returns a ``BNGIndexedRaster`` list given an input raster and BNG resolution.

    A :class:`~osbng.indexing_rio.BNGIndexedRaster` object is created for each BNG
    grid square that intersects with the raster bounds at the specified resolution.

    Args:
        src (rasterio.io.DatasetReader | str): An open Rasterio dataset or a file path
          to a raster.
        resolution (int | str): The BNG resolution expressed either as a metre-based
            integer or as a string label.

    Returns:
        list[BNGIndexedRaster]: A list of ``BNGIndexedRaster`` objects covering the
        raster bounds.

    Raises:
        RasterCRSError: If the raster is not in the British National Grid CRS
          (EPSG:27700).
        BNGExtentError: If the raster bounds are outside the BNG index system
          extent.
        RasterResError: If the raster pixels are not square (equal x and y resolution),
          or if the raster resolution is not a factor of the BNG resolution.
        BNGResolutionError: If an invalid resolution is provided, or if the raster
          resolution is not compatible with the target BNG resolution.
        :class:`~rasterio.errors.RasterioIOError`: If ``src`` is neither a Rasterio
          ``DatasetReader`` nor a valid file path string.

    """
    bng_refs = rst_bounds_to_bng(src, resolution)

    return [BNGIndexedRaster(src, bng_ref) for bng_ref in bng_refs]


def rst_to_bng_intersection_iter(
    dir_path: str,
    resolution: int | str,
    *,
    filename_glob: str = "*.tif*",
    recursive: bool = False,
    as_records: bool = False,
) -> Iterator[BNGIndexedRaster] | Iterator[dict]:
    """Yields chipped ``BNGIndexedRaster`` objects from a directory of raster files.

    For each raster file found in the specified directory (matching the optional glob
    pattern), this function identifies the BNG grid squares that intersect with the
    raster's bounds at the specified resolution. It then yields a
    :class:`~osbng.indexing_rio.BNGIndexedRaster` object for each intersecting grid
    square.

    Notes:
        This function will yield separate ``BNGIndexedRaster``
        objects for each raster file found in the specified directory, even if a BNG
        grid square spans multiple raster files.

    Args:
        dir_path (str): The directory containing raster files to be processed.
        resolution (int|str): The BNG resolution expressed either as a metre-based
            integer or as a string label.

    Keyword Args:
        filename_glob (str): An optional glob pattern to match specific raster files in
          the directory. Defaults to *.tif*
        recursive (bool): Whether to search for files recursively in subdirectories.
          Defaults to False.
        as_records (bool): If True, yields dictionary records instead of
          ``BNGIndexedRaster`` objects. Defaults to False.

    Yields:
        ``BNGIndexedRaster`` | dict: ``BNGIndexedRaster`` objects, or dictionary
        records if ``as_records`` is True.

    Raises:
        NotADirectoryError: If the provided path is not a valid directory.
        FileNotFoundError: If no raster files are found in the directory.
        RasterCRSError: If the raster is not in the British National Grid CRS
          (EPSG:27700).
        BNGExtentError: If the raster bounds are outside the BNG index system
          extent.
        RasterResError: If the raster pixels are not square (equal x and y resolution),
          or if the raster resolution is not a factor of the BNG resolution.
        BNGResolutionError: If an invalid resolution is provided, or if the raster
          resolution is not compatible with the target BNG resolution.
    """
    if not os.path.isdir(dir_path):
        raise NotADirectoryError(
            f"The provided path '{dir_path}' is not a valid directory."
        )

    bng_refs = []
    glob_pattern = filename_glob if filename_glob else "*.tif*"
    # Iterate over all .tif and .tif* files in the directory
    files = glob.iglob(dir_path + "/" + glob_pattern, recursive=recursive)

    # identify if any files exist
    try:
        with rio.open(next(files)) as dataset:
            bng_refs = rst_bounds_to_bng(dataset, resolution)
            for bng_ref in bng_refs:
                if as_records:
                    yield BNGIndexedRaster(dataset, bng_ref).to_record()
                else:
                    yield BNGIndexedRaster(dataset, bng_ref)
    except StopIteration:
        raise FileNotFoundError(
            f"No raster files found in directory '{dir_path}' "
            f"matching pattern '{glob_pattern}'."
        )

    # continue with remaining files
    for raster_file in files:
        with rio.open(raster_file) as dataset:
            bng_refs = rst_bounds_to_bng(dataset, resolution)
            for bng_ref in bng_refs:
                if as_records:
                    yield BNGIndexedRaster(dataset, bng_ref).to_record()
                else:
                    yield BNGIndexedRaster(dataset, bng_ref)
