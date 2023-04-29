#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype PEP-agnostic type hint getter utility** unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.hint.utilhintget` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_get_hint_repr() -> None:
    '''
    Test the :func:`beartype._util.hint.utilhintget.get_hint_repr` getter.
    '''

    # Defer test-specific imports.
    from beartype._util.hint.utilhintget import get_hint_repr
    from beartype_test.a00_unit.data.hint.data_hint import (
        NOT_HINTS, HINTS_NONPEP)
    from beartype_test.a00_unit.data.hint.pep.data_pep import (
        HINTS_PEP_META)

    # Assert this getter returns the expected representations of objects *NOT*
    # supported as either PEP-noncompliant or -compliant type hints.
    for non_hint in NOT_HINTS:
        assert get_hint_repr(non_hint) == repr(non_hint)

    # Assert this getter returns the expected representations of
    # PEP-noncompliant type hints.
    for nonhint_pep in HINTS_NONPEP:
        assert get_hint_repr(nonhint_pep) == repr(nonhint_pep)

    # Assert this getter returns the expected representations of PEP-compliant
    # type hints.
    for hint_pep_meta in HINTS_PEP_META:
        # PEP-compliant type hint to be tested.
        hint_pep = hint_pep_meta.hint

        # Representation of this hint.
        hint_pep_repr = repr(hint_pep)

        # If this representation embeds the representation of a type union,
        # silently ignore this hint and continue to the next. Why? Because
        # Python intentionally hashes both PEP 484-compliant type unions (e.g.,
        # "typing.Union[int, str]") *AND* PEP 604-compliant type unions (e.g.,
        # "int | str") to the same integers. However, these two kinds of unions
        # have fundamentally different representations.
        #
        # Specifically, ignore this hint if this representation embeds the
        # representation of either...
        if (
            # A PEP 484-compliant type union.
            'typing.Union[' in hint_pep_repr or
            # A PEP 604-compliant type union.
            ' | ' in hint_pep_repr
        ):
            continue
        # Else, this representation contains *NO* type union.

        # Assert this getter returns the expected representation.
        assert get_hint_repr(hint_pep) == repr(hint_pep)
