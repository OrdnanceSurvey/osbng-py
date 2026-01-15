"""Configuration file for Sphinx documentation."""

import sys
from datetime import datetime
from pathlib import Path

# Project root directory from docs/
# Represents parent directory of the osbng package
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Add root directory to sys.path
# Ensures Python can import osbng during autodoc
sys.path.insert(0, str(PROJECT_ROOT))

# Project information
project = "osbng"
author = "Ordnance Survey"
copyright = f"{datetime.now().year}, {author}"
release = "0.5.0"

# Sphinx extensions
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    # Jupyter Notebook support
    "nbsphinx",
    # Copy button for code blocks
    "sphinx_copybutton",
]

# Napoleon configuration
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = True

# Only insert the __init__ docstring for class documentation
autoclass_content = "init"

# Templates path
templates_path = ["_templates"]
# Patterns to exclude
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# HTML output configuration
html_theme = "pydata_sphinx_theme"
html_title = "osbng"
html_static_path = ["_static"]
html_theme_options = {
    "logo": {
        "text": "osbng",
        "image_light": "_static/images/os_logo_mono_dark_rgb.svg",
        "image_dark": "_static/images/os_logo_mono_light_rgb.svg",
    },
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/OrdnanceSurvey/osbng-py",
            "icon": "fab fa-github",
            "type": "fontawesome",
        },
    ],
    # Ensure the icon area shows on the right
    "navbar_end": ["theme-switcher", "navbar-icon-links"],
}

# Support cross‑references to objects in external projects
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", "inventories/python.inv"),
    "numpy": ("https://numpy.org/doc/stable/", "inventories/numpy.inv"),
    "shapely": ("https://shapely.readthedocs.io/en/stable/", "inventories/shapely.inv"),
    "geopandas": ("https://geopandas.org/en/stable/", "inventories/geopandas.inv"),
}
