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
def test_claw_this_package() -> None:
    '''
    Test the :mod:`beartype.claw.beartype_this_package` import hook against a
    data subpackage in this test suite exercising *all* edge cases associated
    with this import hook.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.claw._pkg.clawpkgcontext import packages_trie_cleared
    from beartype._util.mod.utilmodget import get_module_dir
    from beartype._util.path.utilpathremove import (
        remove_package_bytecode_files)
    from beartype_test.a00_unit.data import claw

    # ....................{ PATHS                          }....................
    # High-level "Path" object encapsulating the absolute dirname of this module
    # if this module is physically defined on-disk *OR* raise an exception
    # otherwise (i.e., if this module is abstractly defined only in-memory).
    module_dir = get_module_dir(claw)

    # High-level "Path" object encapsulating the "beartype_this_package/"
    # subdirectory directly contained in this parent directory.
    #
    # Note that we intentionally avoid importing the "beartype_this_package"
    # subpackage here. Why? Because doing so would implicitly install the exact
    # beartype import hook which we exercise below and which *MUST* be confined
    # to a context manager for test idempotency.
    subpackage_dir = module_dir / 'beartype_this_package'

    # Remove all previously compiled bytecode files from this subdirectory. Why?
    # Because failing to do so invites subtle but easily reproducible
    # desynchronization woes between those files and more recent changes to our
    # "beartype.claw" implementation. See the
    # remove_package_bytecode_files() docstring for further details.
    remove_package_bytecode_files(subpackage_dir)

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
        #FIXME: Uncomment after worky. *sigh*
        # Defer hooks installing import hooks to this context manager.
        from beartype_test.a00_unit.data.claw.beartype_this_package import (
            this_submodule)
        # pass
