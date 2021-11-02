#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **Sphinx** utilities (i.e., callables handling the third-party
:mod:`sphinx` package as an optional runtime dependency of this project).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To prevent this project from accidentally requiring third-party
# packages as mandatory runtime dependencies, avoid importing from *ANY* such
# package via a module-scoped import. These imports should be isolated to the
# bodies of callables declared below.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from sys import modules as module_imported_names

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ TESTERS                           }....................
#FIXME: Unit test us up, please. See this point for a reasonably simple Sphinx
#directory layout we might consider harvesting inspiration from:
#    https://stackoverflow.com/q/62651201/2809027
#Note that we probably want to use Sphinx's auto-configuration tool to build
#out a simple "conf.py" and directory layout with.
#FIXME: Refactor this to leverage a genuinely valid working solution hopefully
#provided out-of-the-box by some hypothetical new bleeding-edge version of
#Sphinx *AFTER* they resolve our feature request for this:
#    https://github.com/sphinx-doc/sphinx/issues/9805
def is_sphinx_autodocing() -> bool:
    '''
    ``True`` only if Sphinx is currently **autogenerating documentation**
    (i.e., if this function has been called from a Python call stack invoked by
    the ``autodoc`` extension bundled with the optional third-party build-time
    :mod:`sphinx` package).
    '''

    #FIXME: *THIS IS HORRIBLE.* It's also the best we can currently do. See the
    #above issue for further discussion. (We can only shrug ignorantly.)

    # Return true only if the "autodoc" extension has been imported.
    return 'sphinx.ext.autodoc' in module_imported_names
