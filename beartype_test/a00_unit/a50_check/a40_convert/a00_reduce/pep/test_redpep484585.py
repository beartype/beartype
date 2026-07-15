#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype :pep:`484`- and :pep:`585`-compliant **generic reduction** unit
tests.

This submodule unit tests the public API of the private
:mod:`beartype._check.convert._reduce._pep.pep484585.redpep484585generic`
submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ factory                    }....................
def test_reduce_hint_pep484585_generic_subbed() -> None:
    '''
    Test the private
    :func:`beartype._check.convert._reduce._pep.pep484585.redpep484585generic.reduce_hint_pep484585_generic_subbed`
    reducer.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorHintPep484585Exception
    from beartype._check.cls.call.calldataexternal import (
        BEARTYPE_CALL_EXTERNAL_META)
    from beartype._check.convert._reduce._pep.pep484585.redpep484585generic import (
        reduce_hint_pep484585_generic_subbed)
    from beartype_test.a00_unit.data.pep.generic.data_pep585generic import (
        Pep585ListT)
    from beartype_test.a00_unit.data.pep.pep484.data_pep484 import T
    from beartype_test._util.error.pyterrraise import raises_uncached

    # ....................{ PASS                           }....................
    # Assert that this reducer reduces an arbitrary PEP 585-compliant
    # subscripted generic whose unsubscripted form was originally parametrized
    # by one PEP 484-compliant type variable to metadata encapsulating that
    # unsubscripted form *AND* a mapping from that type variable to the single
    # child hint subscripting this subscripted generic.
    hint_sane = reduce_hint_pep484585_generic_subbed(
        call_curr=BEARTYPE_CALL_EXTERNAL_META,
        hint=Pep585ListT[int],
        hint_parent_sane=None,
        exception_prefix='',
    )
    assert hint_sane.hint is Pep585ListT
    assert hint_sane.typearg_to_hint == {T: int}

    # ....................{ FAIL                           }....................
    # Assert this reducer raises the expected exception when the passed object
    # is an invalid PEP 585-compliant subscripted generic (i.e., generic
    # subscripted by more child type hints than the number of type parameters
    # originally parametrizing the unsubscripted form of this generic).
    with raises_uncached(BeartypeDecorHintPep484585Exception):
        reduce_hint_pep484585_generic_subbed(
            call_curr=BEARTYPE_CALL_EXTERNAL_META,
            hint=Pep585ListT[str, bytes],
            hint_parent_sane=None,
            exception_prefix='',
        )
