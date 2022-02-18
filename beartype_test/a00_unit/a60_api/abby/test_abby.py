#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype abby unit tests.**

This submodule unit tests the public API of the public
:mod:`beartype.abby` subpackage.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                             }....................
def test_api_abby_die_if_unbearable_fail() -> None:
    '''
    Test unsuccessful usage of the private
    :class:`beartype.abby.die_if_unbearable` tester.

    Note that the corresponding ``test_api_abby_die_if_unbearable_pass`` test
    resides under the :mod:`beartype_test.a00_unit.a90_decor.main` subpackage
    for orthogonality with other core runtime type-checking unit tests.
    '''

    # Defer heavyweight imports.
    from beartype.abby import die_if_unbearable
    from beartype.roar import (
        BeartypeConfException,
        BeartypeDecorHintNonpepException,
    )
    from pytest import raises

    # Assert this tester raises the expected exception when passed an invalid
    # object as the type hint.
    with raises(BeartypeDecorHintNonpepException):
        die_if_unbearable(
            obj='Holds every future leaf and flower; the bound',
            hint=b'With which from that detested trance they leap;',
        )

    # Assert this tester raises the expected exception when passed an invalid
    # object as the beartype configuration.
    with raises(BeartypeConfException):
        die_if_unbearable(
            obj='The torpor of the year when feeble dreams',
            hint=str,
            conf='Visit the hidden buds, or dreamless sleep',
        )


def test_api_abby_is_bearable_fail() -> None:
    '''
    Test unsuccessful usage of the private
    :class:`beartype.abby.is_bearable` tester.

    Note that the corresponding ``test_api_abby_is_bearable_pass`` test
    resides under the :mod:`beartype_test.a00_unit.a90_decor.main` subpackage
    for orthogonality with other core runtime type-checking unit tests.
    '''

    # Defer heavyweight imports.
    from beartype.abby import is_bearable
    from beartype.roar import (
        BeartypeConfException,
        BeartypeDecorHintNonpepException,
    )
    from pytest import raises

    # Assert this tester raises the expected exception when passed an invalid
    # object as the type hint.
    with raises(BeartypeDecorHintNonpepException):
        is_bearable(
            obj='Holds every future leaf and flower; the bound',
            hint=b'With which from that detested trance they leap;',
        )

    # Assert this tester raises the expected exception when passed an invalid
    # object as the beartype configuration.
    with raises(BeartypeConfException):
        is_bearable(
            obj='The torpor of the year when feeble dreams',
            hint=str,
            conf='Visit the hidden buds, or dreamless sleep',
        )
