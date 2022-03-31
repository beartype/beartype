#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.
#
# --------------------( SYNOPSIS                          )--------------------
# Configuration file for the Sphinx documentation builder.
#
# --------------------( SEE ALSO                          )--------------------
# * https://www.sphinx-doc.org/en/master/usage/configuration.html
#   List of all options supported in this file.

# ....................{ TODO                              }....................
#FIXME: [EXTENSION] Add "intersphinx" support to enable us to cross-reference
#standard modules (e.g., "typing"). Yes, this absolutely should be builtin.
#Naturally, that means it isn't. See also:
#    https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html
#FIXME: [EXTENSION] Add "sphinx-notfound-page" support to enable us to provide
#a sane 404 page for non-existent pages. In fact, we already appear to have a
#"404.rst" document. Well, isn't that noice. Because we can't be bothered to
#configure this at the moment, note that:
#* We've temporarily moved "404.rst" into the parent subdirectory, where it
#  has absolutely no effect (but at least does *NOT* induce fatal errors).
#* We'll need to move "404.rst" back into this subdirectory first.

#FIXME: [THEME] Consider switching to the nascent PyData Sphinx theme, now
#widely leveraged across the data science sphere (e.g., NumPy, SciPy):
#    https://github.com/pydata/pydata-sphinx-theme

#FIXME: [QA] Add one or more pytest-based functional tests exercising this
#configuration. This is slightly less trivial than I'd like, largely as the
#Sphinx team has yet to properly document their "sphinx.testing" system. See
#this pending issue for working code examples:
#    https://github.com/sphinx-doc/sphinx/issues/7008
#
#At the least, we probably need to add the following line to our top-level
#"conftest.py" file:
#    pytest_plugins = 'sphinx.testing.fixtures'
#FIXME: Sadly, nothing has been done to document "sphinx.testing" as of 2022
#Q2. We intuit from perambulating over the "sphinx.testing.fixtures" submodule
#that either the higher-level app() or lower-level make_app() fixtures should
#suffice for our use case. How do we actually configure these fixtures to
#correctly crawl over our specific documentation structure, however?

# ....................{ IMPORTS ~ kludge                  }....................
# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# See also:
# * https://samnicholls.net/2016/06/15/how-to-sphinx-readthedocs
#   The "Make autodoc actually work" is the canonical writeup on this kludge.
# import os, sys
# # sys.path.insert(0, os.path.abspath('../../'))
# print(f'sys.path (from "doc/source/conf.py"): {sys.path}')

# ....................{ IMPORTS                           }....................
# Sphinx defaults to hardcoding version specifiers. Since this is insane, we
# import our package-specific version specifier for reuse below. See also:
# * https://protips.readthedocs.io/git-tag-version.html
#   "Inferring Release Number from Git Tags", detailing a clever one-liner
#   harvesting this specifier from the most recent git tag.
from beartype.meta import AUTHORS, COPYRIGHT, NAME, VERSION
from beartype._util.mod.utilmodtest import is_module
from warnings import warn

# ....................{ METADATA                          }....................
# Metadata programmatically defined by this package.
project = NAME
author = AUTHORS
copyright = COPYRIGHT
release = VERSION

# ....................{ SETTINGS                          }....................
# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files. This pattern also
# affects html_static_path and html_extra_path.
exclude_patterns = []

# ....................{ EXTENSIONS ~ mandatory            }....................
# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = [
    # ..................{ BUILTIN                           }..................
    # Builtin extensions unconditionally available under *ALL* reasonably
    # modern versions of Sphinx uniquely prefixed by "sphinx.ext.".

    # Automatically create one explicit globally cross-referenceable target
    # "{/document/basename}:{section_title}" for each section titled
    # "{section_title}" of each document residing at "{/document/basename}". By
    # default, Sphinx insanely requires targets to be manually prepended before
    # all sections to be cross-referenced elsewhere.
    'sphinx.ext.autosectionlabel',

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

    # ..................{ BUILTIN ~ autodoc                 }..................
    #FIXME: Actually, we probably just want to use the third-party Sphinx
    #AutoAPI extension instead at:
    #    https://github.com/readthedocs/sphinx-autoapi
    #...is what we'd be saying if AutoAPI was still actively maintained. *sigh*
    #FIXME: Almost certainly insufficient. Since this is Sphinx, the
    #"autodoc" extension requires additional non-trivial configuration. Note,
    #however, that the "autosummary" extension enabled below *SHOULD* automate
    #most of that configuration once its fully working. Ergo, avoid investing a
    #considerable amount of effort in "autodoc" itself. Try "autosummary"!

    # Builtin extension autogenerating reStructuredText documentation from
    # class, callable, and variable docstrings embedded in Python modules,
    # documenting this project's public (and optionally also private) API.
    'sphinx.ext.autodoc',

    #FIXME: How does this compare with "viewcode"? Are the two at all
    #comparable? Does merely one suffice? Research us up, please.
    #FIXME: Almost certainly insufficient. Since this is Sphinx, the
    #"autosummary" extension requires additional non-trivial configuration that
    #absolutely *SHOULD* come bundled with Sphinx but currently isn't for
    #nebulous reasons. See this StackOverflow answer for an exhaustive solution
    #requiring copying of third-party templates into our configuration:
    #    https://stackoverflow.com/a/62613202/2809027
    #Lastly, note that this issue may have been resolved by a bleeding-edge
    #Sphinx version by the time we finally resolve this. See also the end of:
    #    https://github.com/sphinx-doc/sphinx/issues/7912

    # Builtin extension autosummarizing reStructuredText documentation
    # autogenerated by the "autodoc" extension (listed above). By default,
    # the "autodoc" extension fails to automatically structure (i.e., summarize
    # with a single compact HTML markup tag) the documentation it generates.
    'sphinx.ext.autosummary',

    # ..................{ THIRD-PARTY                       }..................
    # Third-party Sphinx extensions required to be externally installed. For
    # usability, this block should typically be empty. Third-party Sphinx
    # extensions should ideally be optionally enabled. See below.
]

# ....................{ EXTENSIONS ~ optional             }....................
# Third-party Sphinx extensions conditionally used if externally installed.

# If "sphinx_rtd_theme" (i.e., the third-party Sphinx extension providing the
# official Read The Docs (RTD) HTML theme) is importable under the active
# Python interpreter, prefer this theme to Sphinx's default HTML theme for
# substantially more mobile-friendly rendering.
if is_module('sphinx_rtd_theme'):
    # Register the fully-qualified name of this extension.
    extensions.append('sphinx_rtd_theme')

    # Set the HTML theme to this theme.
    html_theme = 'sphinx_rtd_theme'
# Else, this theme extension is unavailable. In this case, fallback to the
# Sphinx's default HTML theme *AND*...
else:
    #FIXME: Convert this back into a warning by calling warn() *AFTER* deciding
    #how to do so safely. The core issue is that we convert warnings into
    #failures during testing; ergo, we need to install the Python package
    #providing this theme during testing. We can't be bothered at the moment.
    # Emit a non-fatal warning informing end users of this fallback.
    print(
        (
            'WARNING: '
            'Optional Sphinx extension "sphinx_rtd_theme" not found; '
            'falling back to default Sphinx HTML theme.'
        ),
    )

# ....................{ EXTENSIONS ~ autodoc              }....................
# 'sphinx.ext.autodoc'-specific settings. See also:
#     https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html

# Instruct "autodoc" to globally append type hints annotating callable
# signatures to the parameters and returns they annotate in the content (i.e.,
# descriptions) of those callables. Note this requires Sphinx >= 4.1.
autodoc_typehints = 'both'

# ....................{ EXTENSIONS ~ autosectionlabel     }....................
# 'sphinx.ext.autosectionlabel'-specific settings. See also:
#     https://www.sphinx-doc.org/en/master/usage/extensions/autosectionlabel.html

# Instruct "autosectionlabel" to uniquify created targets by prefixing
# section titles with document pathnames in these targets. By default, this
# extension ambiguously creates targets as section titles; that simplistic
# scheme fails when two or more documents share the same section titles, a
# common use case that's effectively infeasible to prohibit.
autosectionlabel_prefix_document = True

# ....................{ EXTENSIONS ~ napoleon             }....................
# 'sphinx.ext.napoleon'-specific settings. See also:
#     https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html

# Force Napolean to *ONLY* parse docstrings in the NumPy format used by this
# project. By default, Napolean attempts and often fails to permissively parse
# docstrings in both Google and NumPy formats.
napoleon_numpy_docstring = True
napoleon_google_docstring = False

# List of the names of all non-standard section headers (i.e., headers *NOT*
# already supported out-of-the-box by Napoleon) embedded in docstrings
# throughout this project. By default, Napolean silently ignores *ALL* content
# in non-standard section headers.
#
# See also:
# * This list of all standard section headers:
#   https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html#docstring-sections
napoleon_custom_sections = [
    'Caveats',
    'Design',
    'Motivation',
    'Usage',
]

#FIXME: Experiment with enabling these non-default settings as well.
# napoleon_use_param = False
# napoleon_use_ivar = True

# ....................{ BUILD ~ html                      }....................
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
