#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`484` and :pep:`585` **type hint utility** unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.hint.pep.proposal.pep484585.pep484585` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ tester                     }....................
def test_is_hint_pep484585_tuple_empty() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.proposal.pep484585.pep484585tuple.is_hint_pep484585_tuple_empty`
    tester.
    '''

    # Defer test-specific imports.
    from beartype._util.hint.pep.proposal.pep484585.pep484585tuple import (
        is_hint_pep484585_tuple_empty)
    from typing import Tuple  # <-- intentionally import the PEP 484 variant

    # Assert this tester returns true for PEP 484-compliant empty tuple type
    # hints.
    assert is_hint_pep484585_tuple_empty(Tuple[()]) is True

    # Assert this tester returns false for PEP 484-compliant non-empty tuple
    # type hints.
    assert is_hint_pep484585_tuple_empty(Tuple[int, ...]) is False

    # Assert this tester returns true for PEP 585-compliant empty tuple type
    # hints.
    assert is_hint_pep484585_tuple_empty(tuple[()]) is True

    # Assert this tester returns false for PEP 585-compliant non-empty tuple
    # type hints.
    assert is_hint_pep484585_tuple_empty(tuple[int, ...]) is False

# ....................{ TESTS ~ getter                     }....................
def test_get_hint_pep484585_args() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.proposal.pep484585.pep484585.get_hint_pep484585_args`
    getter.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorHintPep585Exception
    from beartype.typing import (
        Dict,
        List,
    )
    from beartype._util.hint.pep.proposal.pep484585.pep484585 import (
        get_hint_pep484585_args)
    from pytest import raises

    # ....................{ PASS                           }....................
    # Assert this getter returns the expected child type hint for a PEP 484-
    # and 585-compliant type hint properly subscripted by one child type hint.
    assert get_hint_pep484585_args(
        hint=List[bool], args_len=1, exception_prefix='') == bool

    # Assert this getter returns the expected child type hints for a PEP 484-
    # and 585-compliant type hint properly subscripted by two or more child type
    # hints.
    assert get_hint_pep484585_args(
        hint=Dict[str, int], args_len=2, exception_prefix='') == (str, int)

    # ....................{ FAIL                           }....................
    # Assert this tester raises the expected exception for an arbitrary type
    # hint passed invalid argument lengths.
    with raises(AssertionError):
        get_hint_pep484585_args(
            hint='He fled. Red morning dawned upon his flight,',
            args_len=0.01,
            exception_prefix='',
        )
    with raises(AssertionError):
        get_hint_pep484585_args(
            hint='Shedding the mockery of its vital hues',
            args_len=0,
            exception_prefix='',
        )

    # Assert this tester raises the expected exception for a PEP
    # 585-compliant dictionary type hint improperly subscripted by an
    # unexpected number of child type hints.
    with raises(BeartypeDecorHintPep585Exception):
        get_hint_pep484585_args(
            hint=Dict[str], args_len=2, exception_prefix='')
