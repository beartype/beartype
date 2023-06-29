#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **current package import hook unit tests** (i.e., unit tests exercising
the :mod:`beartype.claw.beartype_this_package` import hook).
'''

# ....................{ IMPORTS                            }....................
#FIXME: Isolate each unit test defined below to its own subprocess. Why? Module
#imports. Since each unit test defined below tends to reimport the same (or, at
#least, similar) modules as previously run unit tests defined below, module
#imports and thus unit tests *MUST* be isolated to their own subprocesses to
#ensure that these tests may be run in any arbitrary order. See also this astute
#GitHub comment for a related third-party "pytest" plugin; although we do *NOT*
#want to adopt that plugin, this comment provides an awesome snippet that we can
#presumably copy-paste into this test suite to conditionally enable test
#isolation on a test-by-test basis:
#    https://github.com/ansible/pytest-mp/issues/15#issuecomment-1342682418

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
    # Implicitly subject this single package to a beartype import hook
    # configured by a non-default beartype configuration, installed by importing
    # *ANYTHING* from this package.
    from beartype_test.a00_unit.data.claw.hookable_package.beartype_this_package import (
        this_submodule)

    # Import an arbitrary submodule *NOT* subject to that import hook.
    from beartype_test.a00_unit.data.claw import unhookable_module


def test_claw_beartype_package() -> None:
    '''
    Test the :mod:`beartype.claw.beartype_package` import hook against a data
    subpackage in this test suite exercising *all* edge cases associated with
    this import hook.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.claw import beartype_package

    # ....................{ HOOKS                          }....................
    # Explicitly subject this single package to a beartype import hook
    # configured by the default beartype configuration.
    beartype_package('beartype_test.a00_unit.data.claw.hookable_package')

    # Import all submodules of the package hooked above, exercising that these
    # submodules are subject to that import hook.
    from beartype_test.a00_unit.data.claw.hookable_package import pep526_module
    from beartype_test.a00_unit.data.claw.hookable_package.hookable_subpackage import (
        class_submodule,
        func_submodule,
    )

    # Import an arbitrary submodule *NOT* subject to those import hooks.
    from beartype_test.a00_unit.data.claw import unhookable_module

    # ....................{ PASS                           }....................
    #FIXME: Exercise the beartype_package() with additional asserts of all
    #possible edge cases.

    # ....................{ FAIL                           }....................
