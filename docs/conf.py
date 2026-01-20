
import os
import sys
sys.path.insert(0, os.path.abspath('..'))

project = 'Common Energy System Domain Model'
author = 'Research Center for Energy Networks - ETH Zürich'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'myst_parser',
    'nbsphinx',
]

source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

master_doc = 'index'

html_theme = 'sphinx_rtd_theme'
html_theme_options = {
    'collapse_navigation': False,
    'navigation_depth': 3,
    'sticky_navigation': True,
    'titles_only': False,
}

html_static_path = ['_static']
html_css_files = ['css/custom.css']

autodoc_member_order = 'bysource'
autodoc_inherit_docstrings = True
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
autodoc_typehints = 'description'
