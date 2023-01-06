#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.


'''
:mod:`pytest` **Sphinx test plugin** (i.e., early-time configuration guaranteed
to be run by :mod:`pytest` *after* passed command-line arguments are parsed).

:mod:`pytest` implicitly imports *all* functionality defined by this module
into *all* submodules of this subpackage.
'''

# ....................{ IMPORTS                            }....................
# Attempt to...
try:
    # Import the Sphinx-specific make_app() fixture required to portably test
    # Sphinx documentation builds.
    #
    # Note that the Sphinx-specific test_params() fixture is imported *ONLY* to
    # expose that fixture to make_app(), which requires that fixture.
    from sphinx.testing.fixtures import (
        make_app,
        test_params,
    )
except:
    pass
