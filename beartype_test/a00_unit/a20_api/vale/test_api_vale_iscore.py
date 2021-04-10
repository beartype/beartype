#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype core data validation unit tests.**

This submodule unit tests the subset of the public API of the
:mod:`beartype.vale` subpackage defined by the private
:mod:`beartype.vale._valeiscore` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from pytest import raises

# ....................{ TESTS ~ class                     }....................
def test_api_vale_classes_pass() -> None:
    '''
    Test successful usage of the public :mod:`beartype.vale.AnnotatedIs` and
    :mod:`beartype.vale.Is` classes.
    '''

    # Defer heavyweight imports.
    from beartype.vale import AnnotatedIs, Is

    # Objects produced by subscripting the "Is" class with valid validators.
    IsLengthy = Is[lambda text: len(text) > 30]
    IsSentence = Is[lambda text: text and text[-1] == '.']
    IsQuoted = Is[lambda text: '"' in text or "'" in text]

    # Assert these objects satisfy the expected API.
    assert isinstance(IsLengthy, AnnotatedIs)

    # Assert these objects perform the expected validation.
    assert IsLengthy.is_valid('Plunged in the battery-smoke') is False
    assert IsLengthy.is_valid('Right through the line they broke;') is True
    assert IsSentence.is_valid('Theirs not to make reply,') is False
    assert IsSentence.is_valid('Theirs but to do and die.') is True
    assert IsQuoted  .is_valid('Theirs not to reason why,') is False
    assert IsQuoted  .is_valid('"Forward, the Light Brigade!"') is True

    # Object synthesized from the above objects with the domain-specific
    # language (DSL) supported by those objects.
    IsLengthyOrUnquotedSentence = IsLengthy | (IsSentence & ~IsQuoted)

    # Assert this object performs the expected validation.
    assert IsLengthyOrUnquotedSentence.is_valid(
        'Stormed at with shot and shell,') is True
    assert IsLengthyOrUnquotedSentence.is_valid(
        'Rode the six hundred.') is True
    assert IsLengthyOrUnquotedSentence.is_valid(
        '"Forward, the Light Brigade.') is False
    assert IsLengthyOrUnquotedSentence.is_valid(
        'Into the valley of Death') is False


def test_api_vale_classes_fail() -> None:
    '''
    Test successful usage of the public :mod:`beartype.vale.AnnotatedIs` and
    :mod:`beartype.vale.Is` classes.
    '''

    # Defer heavyweight imports.
    from beartype.roar import BeartypeAnnotatedIsCoreException
    from beartype.vale import Is

    # Assert that instantiating the "Is" class raises the expected exception.
    with raises(BeartypeAnnotatedIsCoreException):
        Is()

    # Assert that subscripting the "Is" class with the empty tuple raises the
    # expected exception.
    with raises(BeartypeAnnotatedIsCoreException):
        Is[()]

    # Assert that subscripting the "Is" class with two or more arguments raises
    # the expected exception.
    with raises(BeartypeAnnotatedIsCoreException):
        Is['Cannon to right of them,', 'Cannon to left of them,']

    # Assert that subscripting the "Is" class with a non-callable argument
    # raises the expected exception.
    with raises(BeartypeAnnotatedIsCoreException):
        Is['Cannon in front of them']

    # Assert that subscripting the "Is" class with a C-based callable argument
    # raises the expected exception.
    with raises(BeartypeAnnotatedIsCoreException):
        Is[iter]

    # Assert that subscripting the "Is" class with a pure-Python callable that
    # does *NOT* accept exactly one argument raises the expected exception.
    with raises(BeartypeAnnotatedIsCoreException):
        Is[lambda: True]

    # Assert that subscripting the "Is" class with a pure-Python callable that
    # does *NOT* accept exactly one argument raises the expected exception.
    with raises(BeartypeAnnotatedIsCoreException):
        Is[lambda: True]

    # Object produced by subscripting the "Is" class with a valid validator.
    IsNonEmpty = Is[lambda text: bool(text)]

    # Assert that attempting to synthesize new objects from the above object
    # with the domain-specific language (DSL) supported by that object and an
    # arbitrary object that is *NOT* an instance of the same class raises the
    # expected exception.
    with raises(BeartypeAnnotatedIsCoreException):
        IsNonEmpty & 'While horse and hero fell.'
    with raises(BeartypeAnnotatedIsCoreException):
        IsNonEmpty | 'While horse and hero fell.'

# ....................{ TESTS ~ tester                    }....................
def test_api_vale_is_hint_pep593_beartype() -> None:
    '''
    Test usage of the private
    :mod:`beartype.vale._valeiscore.is_hint_pep593_beartype` tester.
    '''

    # Defer heavyweight imports.
    from beartype.roar import BeartypeDecorHintPepException
    from beartype.vale._valeiscore import Is, is_hint_pep593_beartype
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_9

    # If the active Python interpreter targets at least Python >= 3.9 and thus
    # supports PEP 593...
    if IS_PYTHON_AT_LEAST_3_9:
        from typing import Annotated

        # Assert this tester accepts beartype-specific metahints.
        assert is_hint_pep593_beartype(Annotated[
            str, Is[lambda text: bool(text)]]) is True

        # Assert this tester rejects beartype-agnostic metahints.
        assert is_hint_pep593_beartype(Annotated[
            str, 'And may there be no sadness of farewell']) is False

    # Assert this tester raises the expected exception when passed a
    # non-metahint in either case.
    with raises(BeartypeDecorHintPepException):
        is_hint_pep593_beartype('When I embark;')
