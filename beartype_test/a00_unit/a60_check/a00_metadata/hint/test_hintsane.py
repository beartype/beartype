#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype sanified type hint metadata dataclass** unit tests.

This submodule unit tests the :func:`beartype._check.metadata.hint.hintsane`
submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_hintsane() -> None:
    '''
    Test the
    :func:`beartype._check.metadata.hint.hintsane.HintSane` dataclass.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._check.metadata.hint.hintsane import (
        HINT_SANE_IGNORABLE,
        HINT_SANE_RECURSIVE,
        HintSane,
    )

    # ....................{ ASSERTS                        }....................
    # Assert these metadata singletons to be genuinely unique objects.
    assert HINT_SANE_IGNORABLE is not HINT_SANE_RECURSIVE

    # Assert that the metaclass of the "HintSane" type successfully:
    # * Memoizes attempts to re-instantiate that type against the same hint when
    #   passed *NO* optional keyword parameters.
    # * Does *NOT* memoizes attempts to re-instantiate that type against the
    #   same hint when passed one or more optional keyword parameters.
    assert HintSane(list[str]) is HintSane(list[str])
    assert (
        HintSane(list[str], is_unmemoized=True) is not
        HintSane(list[str], is_unmemoized=True)
    )
