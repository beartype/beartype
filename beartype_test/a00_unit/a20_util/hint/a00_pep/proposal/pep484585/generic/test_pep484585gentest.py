#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`484` and :pep:`585` **generic type hint tester** unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.hint.pep.proposal.pep484585.generic.pep484585gentest`
submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ testers                    }....................
def test_is_hint_pep484585_generic(hints_pep_meta) -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.proposal.pep484585.generic.pep484585gentest.is_hint_pep484585_generic`
    tester.

    Parameters
    ----------
    hints_pep_meta : List[beartype_test.a00_unit.data.hint.util.data_hintmetacls.HintPepMetadata]
        List of PEP-compliant type hint metadata describing sample PEP-compliant
        type hints exercising edge cases in the :mod:`beartype` codebase.
    '''

    # Defer test-specific imports.
    from beartype._data.hint.pep.sign.datapepsignset import HINT_SIGNS_GENERIC
    from beartype._util.hint.pep.proposal.pep484585.generic.pep484585gentest import (
        is_hint_pep484585_generic)
    from beartype_test.a00_unit.data.hint.data_hint import NOT_HINTS_PEP

    # Assert this tester:
    # * Accepts generic PEP 484-compliant generics.
    # * Rejects concrete PEP-compliant type hints.
    for hint_pep_meta in hints_pep_meta:
        assert is_hint_pep484585_generic(hint_pep_meta.hint) is (
            hint_pep_meta.pep_sign in HINT_SIGNS_GENERIC)

    # Assert this tester rejects non-PEP-compliant type hints.
    for not_hint_pep in NOT_HINTS_PEP:
        assert is_hint_pep484585_generic(not_hint_pep) is False


def test_is_hint_pep484585_generic_unsubscripted(hints_pep_meta) -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.proposal.pep484585.generic.pep484585gentest.is_hint_pep484585_generic_unsubscripted`
    tester.

    Parameters
    ----------
    hints_pep_meta : List[beartype_test.a00_unit.data.hint.util.data_hintmetacls.HintPepMetadata]
        List of PEP-compliant type hint metadata describing sample PEP-compliant
        type hints exercising edge cases in the :mod:`beartype` codebase.
    '''

    # Defer test-specific imports.
    from beartype._data.hint.pep.sign.datapepsigns import (
        HintSignPep484585GenericUnsubscripted)
    from beartype._util.hint.pep.proposal.pep484585.generic.pep484585gentest import (
        is_hint_pep484585_generic_unsubscripted)
    from beartype_test.a00_unit.data.hint.data_hint import NOT_HINTS_PEP

    # Assert this tester:
    # * Accepts generic PEP 484-compliant generics.
    # * Rejects concrete PEP-compliant type hints.
    for hint_pep_meta in hints_pep_meta:
        # print(f'hint_pep_meta: {repr(hint_pep_meta)}')
        assert is_hint_pep484585_generic_unsubscripted(hint_pep_meta.hint) is (
            hint_pep_meta.pep_sign is HintSignPep484585GenericUnsubscripted)

    # Assert this tester rejects non-PEP-compliant type hints.
    for not_hint_pep in NOT_HINTS_PEP:
        assert is_hint_pep484585_generic_unsubscripted(not_hint_pep) is False


def test_is_hint_pep484585_generic_subscripted(hints_pep_meta) -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.proposal.pep484585.generic.pep484585gentest.is_hint_pep484585_generic_subscripted`
    tester.

    Parameters
    ----------
    hints_pep_meta : List[beartype_test.a00_unit.data.hint.util.data_hintmetacls.HintPepMetadata]
        List of PEP-compliant type hint metadata describing sample PEP-compliant
        type hints exercising edge cases in the :mod:`beartype` codebase.
    '''

    # Defer test-specific imports.
    from beartype._data.hint.pep.sign.datapepsigns import (
        HintSignPep484585GenericSubscripted)
    from beartype._util.hint.pep.proposal.pep484585.generic.pep484585gentest import (
        is_hint_pep484585_generic_subscripted)
    from beartype_test.a00_unit.data.hint.data_hint import NOT_HINTS_PEP

    # Assert this tester:
    # * Accepts generic PEP 484-compliant generics.
    # * Rejects concrete PEP-compliant type hints.
    for hint_pep_meta in hints_pep_meta:
        # print(f'hint_pep_meta: {repr(hint_pep_meta)}')
        assert is_hint_pep484585_generic_subscripted(hint_pep_meta.hint) is (
            hint_pep_meta.pep_sign is HintSignPep484585GenericSubscripted)

    # Assert this tester rejects non-PEP-compliant type hints.
    for not_hint_pep in NOT_HINTS_PEP:
        assert is_hint_pep484585_generic_subscripted(not_hint_pep) is False

# ....................{ TESTS ~ testers : user             }....................
def test_is_hint_pep484585_generic_user(hints_pep_meta) -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.proposal.pep484585.generic.pep484585gentest.is_hint_pep484585_generic_user`
    tester.

    Parameters
    ----------
    hints_pep_meta : List[beartype_test.a00_unit.data.hint.util.data_hintmetacls.HintPepMetadata]
        List of PEP-compliant type hint metadata describing sample PEP-compliant
        type hints exercising edge cases in the :mod:`beartype` codebase.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._util.hint.pep.proposal.pep484585.generic.pep484585gentest import (
        is_hint_pep484585_generic,
        is_hint_pep484585_generic_user,
    )
    from beartype.typing import (
        Generic,
        Protocol,
        Sequence,
        TypeVar,
    )

    # ....................{ TYPEVARS                       }....................
    # Arbitrary unconstrained type variables referenced below.
    T = TypeVar('T')

    # ....................{ LOCALS                         }....................
    # Tuple of zero or more generics that are *NOT* user-defined by third-party
    # logic residing outside the standard Python library.
    GENERICS_NONUSER = (
        Generic,
        Generic[T],
        Protocol,
        Protocol[T],
        Sequence[T],
    )

    # ....................{ ASSERTS                        }....................
    # Assert this tester rejects all non-user-defined generics.
    for generic_nonuser in GENERICS_NONUSER:
        assert is_hint_pep484585_generic_user(generic_nonuser) is False

    # Assert this tester accepts all user-defined generics.
    for hint_pep_meta in hints_pep_meta:
        generic_user = hint_pep_meta.hint
        assert is_hint_pep484585_generic_user(generic_user) is (
               is_hint_pep484585_generic(generic_user))
