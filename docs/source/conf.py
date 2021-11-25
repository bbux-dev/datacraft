# Configuration file for the Sphinx documentation builder.
import os
import sys
sys.path.insert(0, os.path.abspath('../../datagen/'))
# -- Project information

project = 'Datagen'
copyright = '2021, Brian Buxton'
author = 'Brian Buxton'

release = '0.1'
version = '0.1.0'

# -- General configuration

extensions = [
    'sphinx.ext.duration',
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx_copybutton',
    'sphinx_toolbox.collapse',
    'sphinx_autodoc_typehints',
    'sphinx_tabs.tabs',
    'myst_parser'  # for parsing Markdown files
]

templates_path = ['_templates']

# -- Options for HTML output
html_theme = 'sphinx_rtd_theme'

# -- Options for EPUB output
epub_show_urls = 'footnote'
