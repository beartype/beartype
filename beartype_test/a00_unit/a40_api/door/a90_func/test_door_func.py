#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **Decidedly Object-Oriented Runtime-checking (DOOR) procedural API**
unit tests.

This submodule unit tests the subset of the public API of the public
:mod:`beartype.door` subpackage that is procedural.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ testers                    }....................
def test_door_is_subhint(
    door_cases_is_subhint: 'Iterable[Tuple[object, object, bool]]') -> None:
    '''
    Test the :func:`beartype.door.is_subhint` tester.

    Parameters
    ----------
    door_cases_is_subhint : Iterable[Tuple[object, object, bool]]
        Iterable of **type subhint cases** (i.e., 3-tuples ``(subhint,
        superhint, is_subhint)`` describing the subhint relations between two
        type hints).
    '''

    # Defer test-specific imports.
    from beartype.door import is_subhint

    # For each type subhint case to be tested...
    for subhint, superhint, IS_SUBHINT in door_cases_is_subhint:
        # Assert this tester returns the expected boolean for these hints.
        assert is_subhint(subhint, superhint) is IS_SUBHINT
