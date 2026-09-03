#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Test-wide **circular submodule import**
:func:`beartype._util.module.utilmodtest.is_module_initted_partial` data
submodule.

This submodule asserts that the
:func:`beartype._util.module.utilmodtest.is_module_initted_partial` tester
reports the module currently being imported to be only partially initialized
(i.e., returns :data:`True` when passed the fully-qualified name of that same
current from global scope).
'''

# ....................{ IMPORTS                            }....................
from beartype._util.bear.utilbearpackage import is_module_initted_partial

# ....................{ ASSERTS                            }....................
# Assert that this tester reports the module currently being imported to be only
# partially initialized (i.e., *NOT* fully imported yet).
assert is_module_initted_partial(__name__) is True

# Intentionally delete the module spec currently being defined by standard
# "importlib" machinery during the importation of this submodule. Yeah. We know.
del __spec__

# Assert that this tester reports the module currently being imported to now be
# fully initialized (i.e., imported). Yeah. We know. Not our fault, bro. *shrug*
assert is_module_initted_partial(__name__) is False
