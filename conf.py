"""
Sphinx configuration file.
"""
import os
import sys
from datetime import datetime

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath('..'))

# Project information
project = 'Alpha-to-Execution (A2E)'
copyright = f'{datetime.now().year}, Your Name'
author = 'Your Name'
release = '0.1.0'

# General configuration
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.mathjax',
    'sphinx.ext.ifconfig',
    'sphinx.ext.inheritance_diagram',
    'sphinx.ext.graphviz',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# HTML output options
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_theme_options = {
    'navigation_depth': 4,
    'collapse_navigation': False,
    'sticky_navigation': True,
    'includehidden': True,
    'titles_only': False,
}

# Autodoc settings
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__',
}

# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = True
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = True
napoleon_use_ivar = True
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_type_aliases = None

# Intersphinx settings
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
    'pandas': ('https://pandas.pydata.org/docs/', None),
    'torch': ('https://pytorch.org/docs/stable/', None),
    'scikit-learn': ('https://scikit-learn.org/stable/', None),
}

# Graphviz settings
graphviz_output_format = 'svg'
graphviz_dot_args = [
    '-Grankdir=LR',
    '-Gnodesep=0.75',
    '-Gsplines=ortho',
    '-Gconcentrate=true',
    '-Gordering=out',
    '-Granksep=0.75',
]

# Todo settings
todo_include_todos = True

# Coverage settings
coverage_skip_undoc_in_source = True
coverage_ignore_classes = True
coverage_ignore_functions = True
coverage_ignore_modules = True
coverage_ignore_patterns = []
coverage_ignore_calls = []
coverage_ignore_imports = True
coverage_ignore_errors = True
coverage_ignore_names = []
coverage_ignore_undoc = True
coverage_ignore_undoc_in_source = True
coverage_ignore_undoc_in_test = True
coverage_ignore_undoc_in_setup = True
coverage_ignore_undoc_in_build = True
coverage_ignore_undoc_in_docs = True
coverage_ignore_undoc_in_examples = True
coverage_ignore_undoc_in_benchmarks = True
coverage_ignore_undoc_in_scripts = True
coverage_ignore_undoc_in_tools = True
coverage_ignore_undoc_in_utils = True
coverage_ignore_undoc_in_config = True
coverage_ignore_undoc_in_data = True
coverage_ignore_undoc_in_models = True
coverage_ignore_undoc_in_analytics = True
coverage_ignore_undoc_in_execution = True
coverage_ignore_undoc_in_backtest = True
coverage_ignore_undoc_in_risk = True
coverage_ignore_undoc_in_tests = True 