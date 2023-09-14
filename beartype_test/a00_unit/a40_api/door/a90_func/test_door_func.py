#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype Decidedly Object-Oriented Runtime-checking (DOOR) API procedural
unit tests.**

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
    door_cases_subhint: 'Iterable[Tuple[object, object, bool]]') -> None:
    '''
    Test the :func:`beartype.door.is_subhint` tester.

    Parameters
    ----------
    door_cases_subhint : Iterable[Tuple[object, object, bool]]
        Iterable of one or more 3-tuples ``(subhint, superhint, is_subhint)``,
        declared by the :func:`hint_subhint_cases` fixture.
    '''

    # Defer test-specific imports.
    from beartype.door import is_subhint

    # For each subhint relation to be tested...
    for subhint, superhint, IS_SUBHINT in door_cases_subhint:
        # Assert this tester returns the expected boolean for these hints.
        assert is_subhint(subhint, superhint) is IS_SUBHINT
