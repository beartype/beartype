#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **import hook testers** (i.e., low-level callables generically
introspecting the *entire* :mod:`beartype.claw` subpackage as a whole).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# CAUTION: Avoid importing *ANYTHING* from the "beartype" codebase *ANYWHERE*
# inside this submodule. Doing so could induce an accidental circular import,
# due to the tester defined below being transitively called by the
# beartype.claw._importlib._clawimpfileloader.BeartypeSourceFileLoader.get_code()
# method, itself transitively called by standard "importlib" machinery on
# *EVERY* import throughout the active Python process. Manually inline *ALL*
# functionality required by that tester directly into the body of that tester.
# The sole exceptions are:
# * The "beartype._util.module.utilmodinit" submodule, which has been
#   intentionally defined in a similar safe manner as this submodule.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype._util.module.utilmodinitted import is_module_initted_partial

# ....................{ TESTERS                            }....................
def is_beartype_claw_initted_partial() -> bool:
    '''
    :data:`True` only if the :mod:`beartype.claw` subpackage is only **partially
    initialized** (i.e., is currently in the process of being imported by
    standard :mod:`importlib` machinery under the current call stack but has yet
    to be fully imported).
    '''

    # Return true only if this private low-level submodule is only partially
    # initialized. Although low-level, that submodule underlies the entirety of
    # the "beartype.claw" subpackage. There effectively exists a one-to-one
    # relation between that submodule and "beartype.claw" with respect to
    # partial initialization:
    # * If that submodule is only partially initialized, the entire
    #   "beartype.claw" subpackage *MUST* also be only partially initialized.
    # * If the entire "beartype.claw" subpackage is only partially initialized,
    #   that submodule *MUST* also be only partially initialized.
    #
    # The initialization status of that submodule is thus a reasonable proxy for
    # the initialization status of the entire "beartype.claw" subpackage. Maybe.
    return is_module_initted_partial('beartype.claw._clawstate')
