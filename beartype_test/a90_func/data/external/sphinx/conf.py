# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# Note that this is mandatory. If absent, the "autodoc" extension enabled below
# fails with the following build-time error:
#     autodoc: failed to import module 'beartype_sphinx'; the following exception was raised:
#     No module named 'beartype_sphinx'
import os
import sys
sys.path.insert(0, os.path.abspath('.'))

# -- Project information -----------------------------------------------------

project = 'beartype_sphinx'
copyright = '2021, @leycec'
author = '@leycec'

# The full version, including alpha/beta/rc tags
release = '0.0.1'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    # ..................{ BUILTIN                            }..................
    # Builtin extensions unconditionally available under *ALL* reasonably
    # modern versions of Sphinx uniquely prefixed by "sphinx.ext.".

    # Builtin extension autogenerating reStructuredText documentation from
    # class, callable, and variable docstrings embedded in Python modules,
    # documenting this project's public (and optionally also private) API.
    'sphinx.ext.autodoc',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'alabaster'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# ....................{ TESTS                              }....................
#FIXME: Ugh! This decoration raises non-human-readable exceptions. The culprit
#appears to be PEP 563. For unknown reasons, Sphinx appears to be forcing PEP
#563 for this file in a subversive way. Since this file does *NOT* contain an
#actual "from futures import __annotations__" line, @beartype fails to detect
#that Sphinx has activated PEP 563. The result is pure chaos. We'll probably
#have to do something insane like either:
#* Detect when @beartype is running under Sphinx. We already do that, don't we?
#  Sadly, that detection appears to be failing when run from a "conf.py" file.
#  If that detection actually worked, then this decoration would just silently
#  reduce to a noop -- but it's not, so it's not. *shrug*
#* Detect if the name of the calling script is "conf.py". Ugh! This is terrible.
#
#Clearly, the right thing to do is just reduce @beartype to a noop when run from
#this file -- because the alternative is madness. Ergo, we need to improve our
#Sphinx detection to also detect this file. Shouldn't be terribly arduous... or
#it might be, because Sphinx appears to be exec()-ing this file. (Madness!)
#Still, there should be some deterministic remnant of this perfidious behaviour
#on the call stack, we should think. *sigh*

# from beartype import beartype
#
# @beartype
# def sphinx_conf_beartyped_func() -> str:
#     '''
#     Arbitrary callable annotated by one or more arbitrary type hints.
#
#     This callable exercises an edge case in the :mod:`beartype` codebase in
#     which decorating callables defined in Sphinx-specific ``conf.py`` files
#     previously caused :mod:`beartype` to raise non-human-readable exceptions.
#     '''
#
#     return 'Bother-free is the way to be.'
#
# # Call this function to ensure that it is, indeed, callable.
# sphinx_conf_beartyped_func()
