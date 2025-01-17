#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype configuration hint overrides unit tests.**

This submodule unit tests the public :class:`beartype.BeartypeHintOverrides`
class.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_conf_overrides() -> None:
    '''
    Test the public :func:`beartype.BeartypeHintOverrides` class.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype import BeartypeHintOverrides
    from beartype.roar import BeartypeHintOverridesException
    from beartype.typing import (
        List,
        Tuple,
    )
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_10
    from numbers import Real
    from pytest import raises

    # ....................{ LOCALS                         }....................
    # Problematic hint overrides containing one or more recursive hint overrides
    # (which currently induce infinite recursion during code generation) *OTHER*
    # than recursive union hint overrides (which are explicitly supported).
    hint_overrides_bad = {
        # Valid non-recursive hint override.
        float: Real,
    }

    # If the active Python interpreter targets Python >= 3.10 and thus supports
    # PEP 604-compliant new unions...
    if IS_PYTHON_AT_LEAST_3_10:
        # Valid recursive union hint override, intentionally listed *BEFORE* an
        # invalid recursive non-union hint override. Doing so exercises that
        # @beartype supports the former but *NOT* the latter.
        hint_overrides_bad[complex] = complex | float | int

    # Invalid recursive non-union hint override.
    hint_overrides_bad[List[str]] = Tuple[List[str], ...],

    # ....................{ FAIL                           }....................
    # Assert that the "BeartypeHintOverrides" class raises the expected
    # exception when instantiated with these hint overrides.
    with raises(BeartypeHintOverridesException) as exception_info:
        BeartypeHintOverrides(hint_overrides_bad)

    # Message of the exception raised above.
    exception_message = str(exception_info.value)

    # Assert that this message embeds the machine-readable representation of the
    # invalid recursive non-union type hint in question.
    assert repr(List[str]) in exception_message
