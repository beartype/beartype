#!/usr/bin/env python3
# --------------------( SYNOPSIS                          )--------------------
# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# ....................{ TODO                              }....................
#FIXME: Also define a top-level ".readthedocs.yml" file. See:
#    https://docs.readthedocs.io/en/stable/config-file/v2.html?

# ....................{ IMPORTS                           }....................
# Sphinx defaults to hardcoding version specifiers. Since this is insane, we
# import our package-specific version specifier for reuse below. See also:
# * https://protips.readthedocs.io/git-tag-version.html
#   "Inferring Release Number from Git Tags", detailing a clever one-liner
#   harvesting this specifier from the most recent git tag.
from beartype.meta import VERSION

# ....................{ IMPORTS ~ kludge                  }....................
# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# See also:
# * https://samnicholls.net/2016/06/15/how-to-sphinx-readthedocs
#   The "Make autodoc actually work" is the canonical writeup on this kludge.

#FIXME: Uncomment if actually necessary.
# import os, sys
# sys.path.insert(0, os.path.abspath('..'))

# ....................{ METADATA                          }....................
project = 'beartype'
copyright = '2014-2021 Cecil Curry'
author = 'Cecil Curry, et al.'

# The full version, including alpha/beta/rc tags
release = VERSION

# ....................{ SETTINGS                          }....................
# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

# ....................{ EXTENSIONS                        }....................
# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    # Builtin extensions unconditionally available under *ALL* reasonably
    # modern versions of Sphinx uniquely prefixed by "sphinx.ext.".

    # Builtin extension autogenerating reStructuredText documentation from
    # class, callable, and variable docstrings embedded in Python modules,
    # documenting this project's public (and optionally also private) API.
    'sphinx.ext.autodoc',

    # Builtin extension autogenerating reStructuredText documentation from
    # class, callable, and variable docstrings embedded in Python modules
    # formatted according to either NumPy or Google style.
    #
    # Note this effectively requires 'sphinx.ext.autodoc' to be listed as well.
    'sphinx.ext.napoleon',

    # Builtin extension rendering "math::" directives into HTML-only JavaScript
    # via the third-party MathJax library.
    'sphinx.ext.mathjax',

    # Builtin extension autogenerating reStructuredText documentation listing
    # each of this project's Python modules and linking external references to
    # those modules to these listings.
    'sphinx.ext.viewcode',

    # 3rd party Read The Docs HTML theme for neat and mobile-friendly doc site
    'sphinx_rtd_theme',
]

# ....................{ EXTENSIONS ~ napoleon             }....................
# 'sphinx.ext.napoleon'-specific settings. See also:
# * https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html
#   Official documentation.

# Prevent Napoleon from attempting to erroneously parse docstrings in the
# Google format unused by this project.
napoleon_google_docstring = False

#FIXME: Experiment with enabling these non-default settings as well.
# napoleon_use_param = False
# napoleon_use_ivar = True

# ....................{ BUILD ~ html                      }....................
# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# ....................{ BUILD ~ html : mathjax            }....................
# Remote URI to the top-level "MathJax.js" script providing MathJax. If
# unspecified, the current user *MUST* have MathJax locally installed. Note
# that MathJax is locally installable under:
# * Debian systems with:
#   $ sudo apt install libjs-mathjax
#
# See also:
# * https://docs.mathjax.org/en/v2.7-latest/start.html
#   List of all third-party Content Delivery Networks (CDNs) officially hosting
#   MathJax assets.
mathjax_path="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.7/MathJax.js?config=TeX-MML-AM_CHTML"
