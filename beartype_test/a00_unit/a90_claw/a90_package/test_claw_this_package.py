#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **current package import hook unit tests** (i.e., unit tests exercising
the :mod:`beartype.claw.beartype_this_package` import hook).
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_claw_beartype_this_package() -> None:
    '''
    Test the :mod:`beartype.claw.beartype_this_package` import hook against a
    data subpackage in this test suite exercising *all* edge cases associated
    with this import hook.
    '''

    # Defer test-specific imports.
    from beartype.claw._pkg.clawpkgcontext import packages_trie_cleared

    # With a context manager guaranteeably reverting *ALL* beartype import hooks
    # transitively installed in the body of this context manager...
    #
    # Note that merely importing from the "beartype_this_package" subpackage
    # installs a current package beartype import hook against that subpackage.
    # Ergo, this import *MUST* be deferred to the body of this context manager
    # to guaranteeably revert the installation of this hook *BEFORE* this test
    # returns.
    with packages_trie_cleared():
        #FIXME: Uncomment once worky, please.
        # # Defer hooks installing import hooks to this context manager.
        # from beartype_test.a00_unit.data.claw.beartype_this_package import (
        #     this_submodule)
        pass
