#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **module partially initialized utility** unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.module.utilmodinitted` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ testers                    }....................
def test_is_module_initted_partial() -> None:
    '''
    Test the
    :func:`beartype._util.module.utilmodinitted.is_module_initted_partial`
    tester.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._util.module.utilmodinitted import is_module_initted_partial

    # ....................{ ASSERTS                        }....................
    # Assert that this tester reports an arbitrary module guaranteed to *NOT*
    # exist (and thus *NOT* be importable) to *NOT* be partially initialized.
    assert is_module_initted_partial(
        'for_simple_sheep.and_such.are_daffodils') is False

    # Assert that this tester reports an arbitrary module imported above to
    # *NOT* be only partially initialized.
    assert is_module_initted_partial(
        'beartype._util.module.utilmodtest') is False

    # Lastly, import a test-specific data submodule internally asserting that
    # this same tester reports the module currently being imported to be only
    # partially initialized.
    from beartype_test.a00_unit.data.util.module import data_utilmodule_partial
