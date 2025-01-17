#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **sequence factory** unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.kind.sequence.utilseqmake` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ updaters                   }....................
def test_make_stack() -> None:
    '''
    Test the :func:`beartype._util.kind.sequence.utilseqmake.make_stack`
    function.
    '''

    # Defer test-specific imports.
    from beartype._util.kind.sequence.utilseqmake import make_stack

    # Assert that this factory creates the expected stack from empty iterables,
    # including both empty tuples and lists.
    assert make_stack(()) == make_stack([]) == []

    # Assert that this factory creates the expected stack from non-empty
    # iterables, including both non-empty tuples and lists.
    assert (
        make_stack(('Wan', 'moonlight', 'even', 'to', 'fulness:', 'not', 'a', 'star'))) == (
        make_stack(['Wan', 'moonlight', 'even', 'to', 'fulness:', 'not', 'a', 'star'])) == (
        ['star', 'a', 'not', 'fulness:', 'to', 'even', 'moonlight', 'Wan'])
