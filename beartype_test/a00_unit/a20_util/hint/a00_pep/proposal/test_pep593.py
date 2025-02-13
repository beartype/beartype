#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype** :pep:`593` **utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.hint.pep.proposal.pep593` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ validators                 }....................
def test_die_unless_hint_pep593() -> None:
    '''
    Test the
    :beartype._util.hint.pep.proposal.pep593.die_unless_hint_pep593` validator.
    '''

    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorHintPep593Exception
    from beartype.typing import (
        Annotated,
        Optional,
    )
    from beartype._util.hint.pep.proposal.pep593 import die_unless_hint_pep593
    from pytest import raises

    # Assert this validator avoids raising exceptions for a type hint
    # subscripting this factory.
    die_unless_hint_pep593(Annotated[Optional[str], int])

    # Assert this validator raises the expected exception for an arbitrary
    # PEP-compliant type hint *NOT* subscripting this factory.
    with raises(BeartypeDecorHintPep593Exception):
        die_unless_hint_pep593(Optional[str])

# ....................{ TESTS ~ tester                     }....................
def test_is_hint_pep593_beartype() -> None:
    '''
    Test usage of the private
    :mod:`beartype._util.hint.pep.proposal.pep593.is_hint_pep593_beartype`
    tester.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorHintPepException
    from beartype.typing import Annotated
    from beartype.vale import Is
    from beartype._util.hint.pep.proposal.pep593 import is_hint_pep593_beartype
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_10
    from pytest import raises

    # ....................{ PASS                           }....................
    # Assert this tester rejects beartype-agnostic metahints.
    assert is_hint_pep593_beartype(
        Annotated[str, 'And may there be no sadness of farewell']) is False

    # If the active Python interpreter targets Python >= 3.10, assert this
    # tester accepts a beartype-specific metahint annotated by a beartype
    # validator defined as a lambda function. For unknown reasons, the obsolete
    # Python 3.9-specific implementation of the standard "inspect" module fails
    # to inspect the definition of this lambda function; this then induces
    # unexpected warnings. Although we *COULD* catch these warnings here, it's
    # simpler to simply ignore Python 3.9 for now. Yo! Laziness prevails.
    if IS_PYTHON_AT_LEAST_3_10:
        assert is_hint_pep593_beartype(
            Annotated[str, Is[lambda text: bool(text)]]) is True

    # ....................{ FAIL                           }....................
    # Assert this tester raises the expected exception when passed a
    # non-metahint in either case.
    with raises(BeartypeDecorHintPepException):
        is_hint_pep593_beartype('When I embark;')

# ....................{ TESTS ~ getters                    }....................
def test_get_hint_pep593_metadata() -> None:
    '''
    Test the
    :beartype._util.hint.pep.proposal.pep593.get_hint_pep593_metadata`
    getter.
    '''

    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorHintPep593Exception
    from beartype.typing import (
        Annotated,
        Optional,
    )
    from beartype._util.hint.pep.proposal.pep593 import get_hint_pep593_metadata
    from pytest import raises

    # Assert this getter returns the expected tuple for an arbitrary PEP
    # 593-compliant type hint.
    assert get_hint_pep593_metadata(Annotated[
        Optional[str],
        'Thy', 'caverns', 'echoing', 'to', 'the', "Arve's", 'commotion,'
    ]) == (
        'Thy', 'caverns', 'echoing', 'to', 'the', "Arve's", 'commotion,')

    # Assert this getter raises the expected exception for an arbitrary
    # PEP-compliant type hint *NOT* subscripting this factory.
    with raises(BeartypeDecorHintPep593Exception):
        get_hint_pep593_metadata(Optional[str])


def test_get_hint_pep593_metahint() -> None:
    '''
    Test the
    :beartype._util.hint.pep.proposal.pep593.get_hint_pep593_metahint`
    getter.
    '''

    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorHintPep593Exception
    from beartype.typing import (
        Annotated,
        Optional,
    )
    from beartype._util.hint.pep.proposal.pep593 import get_hint_pep593_metahint
    from pytest import raises

    # Assert this getter returns the expected PEP-compliant type hint for an
    # arbitrary PEP 593-compliant type hint.
    metahint = Optional[int]
    assert get_hint_pep593_metahint(Annotated[
        metahint,
        'A', 'loud', 'lone', 'sound', 'no', 'other', 'sound', 'can', 'tame'
    ]) is metahint

    # Assert this getter raises the expected exception for an arbitrary
    # PEP-compliant type hint *NOT* subscripting this factory.
    with raises(BeartypeDecorHintPep593Exception):
        get_hint_pep593_metahint(metahint)
