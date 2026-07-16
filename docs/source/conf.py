# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'ATLAS API Client'
copyright = '2026, Heloise Stevance'
author = 'Heloise Stevance'

import os
import sys
sys.path.insert(0, os.path.abspath('../../'))

from atlasapiclient import __version__

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
]
# The full version, including alpha/beta/rc tags
release = __version__

templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_book_theme'
html_static_path = ['_static']
html_logo='_static/logo.png'
html_theme_options = {
  "show_toc_level": 4,
  "show_navbar_depth": 4,
}
html_sidebars = {
  "**": ["sbt-sidebar-nav.html"],
}
