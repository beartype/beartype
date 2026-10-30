#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Third-party **Plum** integration tests.

This submodule functionally tests the :mod:`beartype` package against the
third-party :mod:`plum` package.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype_test._util.mark.pytskip import skip_unless_package

# ....................{ TESTS                              }....................
@skip_unless_package('plum')
def test_plum() -> None:
    '''
    Integration test validating that Plum dispatches on parameterized type
    hints using :mod:`beartype.door` for matching and subhint comparisons.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from collections.abc import Sequence
    from plum import Dispatcher, NotFoundLookupError
    from pytest import raises

    # ....................{ CALLABLES                      }....................
    # Isolate these overloads from Plum's global dispatch registry.
    dispatch = Dispatcher()

    @dispatch
    def classify(value: Sequence[int]) -> str:
        return 'sequence of integers'

    @dispatch
    def classify(value: list[int]) -> str:
        return 'list of integers'

    @dispatch
    def classify(value: list[str]) -> str:
        return 'list of strings'

    # ....................{ ASSERTS                        }....................
    # Repeat calls with the same container type but different item types to
    # ensure repeated dispatch respects item types, not just container types.
    # Single-item containers keep these checks deterministic even when
    # beartype only checks one randomly selected item.
    for _ in range(2):
        # Prefer the narrower list hint over the matching sequence hint.
        assert classify([1]) == 'list of integers'
        assert classify(['plum']) == 'list of strings'
        assert classify((1,)) == 'sequence of integers'

        # Reject a container whose item satisfies none of the overloads.
        with raises(NotFoundLookupError):
            classify([1.5])
