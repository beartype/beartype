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

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.claw._pkg.clawpkgcontext import packages_trie_cleared

    # ....................{ HOOKS                          }....................
    # With a context manager guaranteeably reverting *ALL* beartype import hooks
    # transitively installed in the body of this context manager...
    #
    # Note that merely importing from the "beartype_this_package" subpackage
    # installs a current package beartype import hook against that subpackage.
    # Ergo, this import *MUST* be deferred to the body of this context manager
    # to guaranteeably revert the installation of this hook *BEFORE* this test
    # returns.
    with packages_trie_cleared():
        # Defer hooks installing import hooks to this context manager.
        from beartype_test.a00_unit.data.claw.hookable_package.beartype_this_package import (
            this_submodule)

        # Import an arbitrary submodule *NOT* subject to those import hooks.
        from beartype_test.a00_unit.data.claw import unhookable_module


#FIXME: Implement us up, please. Doing so will require:
#* Defining a new "clean_claws" fixture (heh, heh) generalizing the existing
#  bytecode removal functionality defined by the
#  test_claw_beartype_this_package() unit test to iteratively remove *ALL*
#  bytecode files transitively nested (at any subdirectory depth) under the
#  "beartype_test.a00_unit.data.claw.hookable_package" subpackage. Doing so will
#  probably necessitate a recursive directory traversal for sanity.

# def test_claw_beartype_package() -> None:
#     '''
#     Test the :mod:`beartype.claw.beartype_package` import hook against a data
#     subpackage in this test suite exercising *all* edge cases associated with
#     this import hook.
#     '''
#
