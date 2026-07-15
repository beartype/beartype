#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
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

# ....................{ TESTS ~ raisers                    }....................
def test_die_if_hint_pep484585_generic_invalid() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.proposal.pep484585.generic.pep484585gentest.die_if_hint_pep484585_generic_invalid`
    raiser.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorHintPep484585Exception
    from beartype._util.hint.pep.proposal.pep484585.generic.pep484585gentest import (
        die_if_hint_pep484585_generic_invalid)
    from beartype_test.a00_unit.data.pep.generic.data_pep484585generic import (
        Pep484585SequenceUGenericIntTListU)
    from beartype_test.a00_unit.data.pep.pep484.data_pep484 import (
        S,
        T,
    )
    from pytest import raises
    from typing import Generic

    # ....................{ PASS                           }....................
    # Implicitly assert that this raiser raises *NO* exception when passed a
    # valid unsubscripted generic (i.e., which is *ALWAYS* guaranteed by
    # definition to be valid).
    die_if_hint_pep484585_generic_invalid(Pep484585SequenceUGenericIntTListU)

    # Implicitly assert that this raiser raises *NO* exception when passed a
    # valid PEP 484-compliant root subscripted generic (i.e., "typing.Generic"
    # superclass directly parametrized by one or more type parameters).
    die_if_hint_pep484585_generic_invalid(Generic[S, T])

    # Implicitly assert that this raiser raises *NO* exception when passed a
    # valid PEP 585-compliant subscripted generic (i.e., subscripted by less
    # than or equal to the number of child type hints than the number of
    # PEP-compliant type parameters parametrizing the unsubscripted form of this
    # generic).
    die_if_hint_pep484585_generic_invalid(
        Pep484585SequenceUGenericIntTListU[str, bytes])

    # ....................{ FAIL                           }....................
    # Assert that this raiser raises the expected exception when passed a
    # non-generic.
    with raises(BeartypeDecorHintPep484585Exception):
        die_if_hint_pep484585_generic_invalid(int)

    # Assert that this raiser raises the expected exception when passed an
    # invalid PEP 585-compliant subscripted generic (i.e., subscripted by more
    # child type hints than the number of PEP-compliant type parameters
    # originally parametrizing the unsubscripted form of this generic).
    with raises(BeartypeDecorHintPep484585Exception):
        die_if_hint_pep484585_generic_invalid(
            Pep484585SequenceUGenericIntTListU[str, bytes, int])

# ....................{ TESTS ~ testers                    }....................
def test_is_hint_pep484585_generic(hints_piths_pep_meta: (
    'list[beartype_test.a00_unit.data.hint.cls.pith.data_clshintpith.HintPepMetadata]'
)) -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.proposal.pep484585.generic.pep484585gentest.is_hint_pep484585_generic`
    tester.

    Parameters
    ----------
    hints_piths_pep_meta : list[beartype_test.a00_unit.data.hint.cls.pith.data_clshintpith.HintPepMetadata]
        List of PEP-compliant type hint metadata describing sample PEP-compliant
        type hints exercising edge cases in the :mod:`beartype` codebase.
    '''

    # Defer test-specific imports.
    from beartype._data.hint.sign.datahintsignset import HINT_SIGNS_GENERIC
    from beartype._util.hint.pep.proposal.pep484585.generic.pep484585gentest import (
        is_hint_pep484585_generic)
    from beartype_test.a00_unit.data.hint.data_hint import NOT_HINTS_PEP

    # Assert this tester:
    # * Accepts generic PEP 484-compliant generics.
    # * Rejects concrete PEP-compliant type hints.
    for hint_pep_meta in hints_piths_pep_meta:
        assert is_hint_pep484585_generic(hint_pep_meta.hint) is (
            hint_pep_meta.pep_sign in HINT_SIGNS_GENERIC)

    # Assert this tester rejects non-PEP-compliant type hints.
    for not_hint_pep in NOT_HINTS_PEP:
        assert is_hint_pep484585_generic(not_hint_pep) is False


def test_is_hint_pep484585_generic_unsubbed(hints_piths_pep_meta) -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.proposal.pep484585.generic.pep484585gentest.is_hint_pep484585_generic_unsubbed`
    tester.

    Parameters
    ----------
    hints_piths_pep_meta : list[beartype_test.a00_unit.data.hint.cls.pith.data_clshintpith.HintPepMetadata]
        List of PEP-compliant type hint metadata describing sample PEP-compliant
        type hints exercising edge cases in the :mod:`beartype` codebase.
    '''

    # Defer test-specific imports.
    from beartype._data.hint.sign.datahintsigns import (
        HintSignPep484585GenericUnsubbed)
    from beartype._util.hint.pep.proposal.pep484585.generic.pep484585gentest import (
        is_hint_pep484585_generic_unsubbed)
    from beartype_test.a00_unit.data.hint.data_hint import NOT_HINTS_PEP

    # Assert this tester:
    # * Accepts generic PEP 484-compliant generics.
    # * Rejects concrete PEP-compliant type hints.
    for hint_pep_meta in hints_piths_pep_meta:
        # print(f'hint_pep_meta: {repr(hint_pep_meta)}')
        assert is_hint_pep484585_generic_unsubbed(hint_pep_meta.hint) is (
            hint_pep_meta.pep_sign is HintSignPep484585GenericUnsubbed)

    # Assert this tester rejects non-PEP-compliant type hints.
    for not_hint_pep in NOT_HINTS_PEP:
        assert is_hint_pep484585_generic_unsubbed(not_hint_pep) is False


def test_is_hint_pep484585_generic_subbed(hints_piths_pep_meta: (
    'list[beartype_test.a00_unit.data.hint.cls.pith.data_clshintpith.HintPepMetadata]'
)) -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.proposal.pep484585.generic.pep484585gentest.is_hint_pep484585_generic_subbed`
    tester.

    Parameters
    ----------
    hints_piths_pep_meta : list[beartype_test.a00_unit.data.hint.cls.pith.data_clshintpith.HintPepMetadata]
        List of PEP-compliant type hint metadata describing sample PEP-compliant
        type hints exercising edge cases in the :mod:`beartype` codebase.
    '''

    # Defer test-specific imports.
    from beartype._data.hint.sign.datahintsigns import (
        HintSignPep484585GenericSubbed)
    from beartype._util.hint.pep.proposal.pep484585.generic.pep484585gentest import (
        is_hint_pep484585_generic_subbed)
    from beartype_test.a00_unit.data.hint.data_hint import NOT_HINTS_PEP

    # Assert this tester:
    # * Accepts generic PEP 484-compliant generics.
    # * Rejects concrete PEP-compliant type hints.
    for hint_pep_meta in hints_piths_pep_meta:
        # print(f'hint_pep_meta: {repr(hint_pep_meta)}')
        assert is_hint_pep484585_generic_subbed(hint_pep_meta.hint) is (
            hint_pep_meta.pep_sign is HintSignPep484585GenericSubbed)

    # Assert this tester rejects non-PEP-compliant type hints.
    for not_hint_pep in NOT_HINTS_PEP:
        assert is_hint_pep484585_generic_subbed(not_hint_pep) is False

# ....................{ TESTS ~ testers : user             }....................
def test_is_hint_pep484585_generic_user(hints_piths_pep_meta: (
    'list[beartype_test.a00_unit.data.hint.cls.pith.data_clshintpith.HintPepMetadata]'
)) -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.proposal.pep484585.generic.pep484585gentest.is_hint_pep484585_generic_user`
    tester.

    Parameters
    ----------
    hints_piths_pep_meta : list[beartype_test.a00_unit.data.hint.cls.pith.data_clshintpith.HintPepMetadata]
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
    for hint_pep_meta in hints_piths_pep_meta:
        generic_user = hint_pep_meta.hint
        assert is_hint_pep484585_generic_user(generic_user) is (
               is_hint_pep484585_generic(generic_user))
