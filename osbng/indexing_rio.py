"""Index rasters in Rasterio DatasetReader objects against the BNG index system.

Note:
    This module requires the 'Rasterio' (https://github.com/rasterio/rasterio)
    package to be installed.

    To install the required package, use:

        pip install osbng[rasterio]

"""

try:
    import rasterio as rio  # noqa: F401, I001
except ImportError as e:
    raise ImportError(
        "The 'rasterio' package is required to use the 'osbng.indexing_rio' module. "
        "Install it with: pip install osbng[rasterio]"
    ) from e
