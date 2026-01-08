#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`646` and :pep:`692` **type hint utility** unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.hint.pep.proposal.pep646692` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ tester                     }....................
def test_is_hint_pep646_tuple_unpacked_prefix() -> None:
    '''
    Test the private
    :mod:`beartype._util.hint.pep.proposal.pep646692.is_hint_pep646_tuple_unpacked_prefix`
    tester.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._util.hint.pep.proposal.pep646692 import (
        is_hint_pep646_tuple_unpacked_prefix)
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_11

    # ....................{ VERSION                        }....................
    # If the active Python interpreter targets Python >= 3.11 and thus supports
    # PEP 646...
    if IS_PYTHON_AT_LEAST_3_11:
        # Defer version-specific imports.
        from beartype_test.a00_unit.data.pep.data_pep646 import (
            tuple_fixed_str_bytes_unpacked_prefix,
            tuple_fixed_str_bytes_unpacked_subbed,
        )

        # Assert that this tester accepts a PEP 646-compliant prefix-flavoured
        # unpacked tuple hint subscripted by arbitrary child hints.
        assert is_hint_pep646_tuple_unpacked_prefix(
            tuple_fixed_str_bytes_unpacked_prefix) is True

        # Assert that this tester rejects a PEP 646-compliant
        # subscription-flavoured unpacked tuple hint subscripted by arbitrary
        # child hints.
        assert is_hint_pep646_tuple_unpacked_prefix(
            tuple_fixed_str_bytes_unpacked_subbed) is False
    # Else, the active Python interpreter targets Python <= 3.10 and thus fails
    # to support PEP 646.

    # ....................{ FAIL                           }....................
    # Assert this tester rejects PEP 484- and 585-compliant tuple type hints of
    # both fixed- and variable-length variants.
    assert is_hint_pep646_tuple_unpacked_prefix(tuple[int, ...]) is False
    assert is_hint_pep646_tuple_unpacked_prefix(tuple[bool, int, float]) is False

    # Assert this tester rejects unrelated arbitrary objects.
    assert is_hint_pep646_tuple_unpacked_prefix(
        'The Titans fierce, self-hid, or prison-bound,') is False

# ....................{ TESTS ~ getter                     }....................
def test_get_hint_pep_args_unpacked_if_pep646_tuple() -> None:
    '''
    Test the private
    :mod:`beartype._util.hint.pep.proposal.pep646692.get_hint_pep_args_unpacked_if_pep646_tuple`
    getter.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._util.hint.pep.proposal.pep646692 import (
        get_hint_pep_args_unpacked_if_pep646_tuple)
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_11

    # ....................{ VERSION                        }....................
    # If the active Python interpreter targets Python >= 3.11 and thus supports
    # PEP 646...
    if IS_PYTHON_AT_LEAST_3_11:
        # Defer version-specific imports.
        from beartype_test.a00_unit.data.pep.data_pep646 import (
            tuple_fixed_str_bytes_unpacked_prefix,
            tuple_fixed_str_bytes_unpacked_subbed,
            Ts,
            Ts_unpacked_prefix,
            Ts_unpacked_subbed,
        )

        # Assert that this getter passed a PEP 646-compliant unpacked tuple hint
        # subscripted by arbitrary child hints returns the tuple of those child
        # hints, regardless of whether that unpacked tuple hint is either
        # prefix- or subscription-flavoured.
        assert get_hint_pep_args_unpacked_if_pep646_tuple(
            tuple_fixed_str_bytes_unpacked_prefix) == (str, bytes)
        assert get_hint_pep_args_unpacked_if_pep646_tuple(
            tuple_fixed_str_bytes_unpacked_subbed) == (str, bytes)

        # Assert that this getter passed a PEP 646-compliant unpacked type
        # variable tuple returns that type variable tuple hints, regardless of
        # whether that unpacked type variable tuple is either prefix- or
        # subscription-flavoured.
        assert get_hint_pep_args_unpacked_if_pep646_tuple(
            Ts_unpacked_prefix) == (Ts,)
        assert get_hint_pep_args_unpacked_if_pep646_tuple(
            Ts_unpacked_subbed) == (Ts,)
    # Else, the active Python interpreter targets Python <= 3.10 and thus fails
    # to support PEP 646.

    # ....................{ ASSERTS                        }....................
    # Assert that this getter passed a PEP 646-noncompliant standard (i.e.,
    # non-unpacked) tuple hint subscripted by arbitrary child hints returns the
    # tuple of those child hints.
    assert get_hint_pep_args_unpacked_if_pep646_tuple(
        tuple[int, float]) == (int, float)

    # Assert that this getter passed a non-tuple hint subscripted by arbitrary
    # child hints returns the tuple of those child hints.
    assert get_hint_pep_args_unpacked_if_pep646_tuple(
        list[bool, complex]) == (bool, complex)
