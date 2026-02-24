# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
from __future__ import annotations

project = "skZemax"
copyright = "2024, USask-ARG"
author = "USask-ARG"
github_url = "https://github.com/usask-arg/skZemax"

import os

if os.environ.get("READTHEDOCS") == "True":
    nb_execution_mode = "off"
else:
    nb_execution_mode = "auto"   # or "cache" 
autodoc_mock_imports = ["pythonnet", "clr", "winreg", "ZOSAPI_NetHelper", "ZOSAPI", "System"]


# release: str = get_version(project)
release: str = ""
version: str = ".".join(release.split(".")[:2])

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.doctest",
    "sphinx.ext.autosummary",
    "sphinx.ext.coverage",
    "sphinx.ext.mathjax",
    "sphinx.ext.napoleon",
    "myst_nb",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    # "sphinx_copybutton",
    "sphinx_design",
    # "sphinx_examples",
    # "sphinx_tabs.tabs",
    # "sphinx_thebe",
    # "sphinx_togglebutton",
    # "sphinxcontrib.bibtex",
    # "sphinxext.opengraph",
    # For the kitchen sink
    "sphinx.ext.todo",
]

templates_path = ["_templates"]
exclude_patterns = []

autodoc_docstring_signature = True
autodoc_default_options = {
    "members": True,
    "show-inheritance": True,
    "member_order": "groupwise",
}
autoclass_content = "both"


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_book_theme"
html_static_path = ["_static"]
html_css_files = ["locals.css"]

html_theme_options = {
    "github_url": github_url,
    "repository_url": github_url,
    "repository_branch": "main",
    "path_to_docs": "docs/source",
    "use_repository_button": True,
    "use_edit_page_button": True,
    "use_issues_button": True,
}

nb_execution_timeout = 300


myst_enable_extensions = [
    "dollarmath",
    "amsmath",
    "deflist",
    # "html_admonition",
    # "html_image",
    "colon_fence",
    # "smartquotes",
    # "replacements",
    # "linkify",
    # "substitution",
]