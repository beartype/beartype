#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype-generated wrapper function utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.utilfunc.lib.utilbeartypefunc` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ testers                   }....................
def test_is_func_beartyped() -> None:
    '''
    Test the
    :func:`beartype._util.func.mod.utilbeartypefunc.is_func_beartyped` tester.
    '''

    # Defer test-specific imports.
    from beartype import beartype
    from beartype._util.func.mod.utilbeartypefunc import is_func_beartyped

    @beartype
    def where_that_or() -> str:
        '''
        Arbitrary callable decorated by the :func:`beartype.beartype`
        decorator intentionally annotated by one or more arbitrary unignorable
        type hints to prevent that decorator from silently reducing to a noop.
        '''

        return 'In the still cave of the witch Poesy,'

    def thou_art_no_unbidden_guest() -> str:
        '''
        Arbitrary callable *not* decorated by the :func:`beartype.beartype`
        decorator intentionally annotated by one or more arbitrary unignorable
        type hints for parity with the prior callable.
        '''

        return 'Seeking among the shadows that pass by'

    # Assert this tester returns the expected results for these callables.
    assert is_func_beartyped(where_that_or) is True
    assert is_func_beartyped(thou_art_no_unbidden_guest) is False

# ....................{ TESTS ~ setters                   }....................
def test_set_func_beartyped() -> None:
    '''
    Test the
    :func:`beartype._util.func.mod.utilbeartypefunc.set_func_beartyped` tester.
    '''

    # Defer test-specific imports.
    from beartype._util.func.mod.utilbeartypefunc import (
        is_func_beartyped,
        set_func_beartyped,
    )

    def ghosts_of_all_things_that_are() -> str:
        '''
        Arbitrary callable *not* decorated by the :func:`beartype.beartype`
        decorator intentionally annotated by one or more arbitrary unignorable
        type hints to prevent that decorator from silently reducing to a noop.
        '''

        return 'some shade of thee,'

    # Assert this callable to *NOT* be a beartype-decorated wrapper function.
    assert is_func_beartyped(ghosts_of_all_things_that_are) is False

    # Declare this callable to be a beartype-decorated wrapper function.
    set_func_beartyped(ghosts_of_all_things_that_are)

    # Assert this callable to now be a beartype-decorated wrapper function.
    assert is_func_beartyped(ghosts_of_all_things_that_are)
