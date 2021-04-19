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

# ....................{ TODO                              }....................
#FIXME: Unit test the "is_valid_code" and "is_valid_locals" instance variables
#here as well, please.

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype_test.util.mark.pytskip import skip_if_python_version_less_than
from pytest import raises

# ....................{ TESTS ~ class                     }....................
@skip_if_python_version_less_than('3.7.0')
def test_api_vale_core_classes_pass() -> None:
    '''
    Test successful usage of the public :mod:`beartype.vale.SubscriptedIs` and
    :mod:`beartype.vale.Is` classes if the active Python interpreter targets
    Python >= 3.7 (and thus supports the ``__class_getitem__()`` dunder method)
    *or* skip otherwise.
    '''

    # Defer heavyweight imports.
    from beartype.vale import SubscriptedIs, Is

    # Objects produced by subscripting the "Is" class with valid validators.
    IsLengthy = Is[lambda text: len(text) > 30]
    IsSentence = Is[lambda text: text and text[-1] == '.']
    IsQuoted = Is[lambda text: '"' in text or "'" in text]

    # Assert these objects satisfy the expected API.
    assert isinstance(IsLengthy, SubscriptedIs)

    # Assert these objects perform the expected validation.
    assert IsLengthy.is_valid('Plunged in the battery-smoke') is False
    assert IsLengthy.is_valid('Right through the line they broke;') is True
    assert IsSentence.is_valid('Theirs not to make reply,') is False
    assert IsSentence.is_valid('Theirs but to do and die.') is True
    assert IsQuoted.is_valid('Theirs not to reason why,') is False
    assert IsQuoted.is_valid('"Forward, the Light Brigade!"') is True

    # Assert these objects provide neither code nor code locals.
    assert IsLengthy.is_valid_code is None
    assert IsLengthy.is_valid_code_locals is None

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


@skip_if_python_version_less_than('3.7.0')
def test_api_vale_core_classes_fail() -> None:
    '''
    Test unsuccessful usage of the public :mod:`beartype.vale.SubscriptedIs` and
    :mod:`beartype.vale.Is` classes if the active Python interpreter targets
    Python >= 3.7 (and thus supports the ``__class_getitem__()`` dunder method)
    *or* skip otherwise.
    '''

    # Defer heavyweight imports.
    from beartype.roar import BeartypeSubscriptedIsInstantiationException
    from beartype.vale import SubscriptedIs, Is

    # Assert that instantiating the "Is" class raises the expected exception.
    with raises(BeartypeSubscriptedIsInstantiationException):
        Is()

    # Assert that subscripting the "Is" class with the empty tuple raises the
    # expected exception.
    with raises(BeartypeSubscriptedIsInstantiationException):
        Is[()]

    # Assert that subscripting the "Is" class with two or more arguments raises
    # the expected exception.
    with raises(BeartypeSubscriptedIsInstantiationException):
        Is['Cannon to right of them,', 'Cannon to left of them,']

    # Assert that subscripting the "Is" class with a non-callable argument
    # raises the expected exception.
    with raises(BeartypeSubscriptedIsInstantiationException):
        Is['Cannon in front of them']

    # Assert that subscripting the "Is" class with a C-based callable argument
    # raises the expected exception.
    with raises(BeartypeSubscriptedIsInstantiationException):
        Is[iter]

    # Assert that subscripting the "Is" class with a pure-Python callable that
    # does *NOT* accept exactly one argument raises the expected exception.
    with raises(BeartypeSubscriptedIsInstantiationException):
        Is[lambda: True]

    # Assert that subscripting the "Is" class with a pure-Python callable that
    # does *NOT* accept exactly one argument raises the expected exception.
    with raises(BeartypeSubscriptedIsInstantiationException):
        Is[lambda: True]

    # Object produced by subscripting the "Is" class with a valid validator.
    IsNonEmpty = Is[lambda text: bool(text)]

    # Assert that attempting to synthesize new objects from the above object
    # with the domain-specific language (DSL) supported by that object and an
    # arbitrary object that is *NOT* an instance of the same class raises the
    # expected exception.
    with raises(BeartypeSubscriptedIsInstantiationException):
        IsNonEmpty & 'While horse and hero fell.'
    with raises(BeartypeSubscriptedIsInstantiationException):
        IsNonEmpty | 'While horse and hero fell.'

    # Assert that attempting to instantiate the "SubscriptedIs" class with
    # non-string code raises the expected exception.
    with raises(BeartypeSubscriptedIsInstantiationException):
        SubscriptedIs(
            is_valid=lambda text: bool(text),
            is_valid_code=b'Into the jaws of Death,',
            get_repr=lambda: f'Is[lambda text: bool(text)]',
        )

    # Assert that attempting to instantiate the "SubscriptedIs" class with
    # empty string code raises the expected exception.
    with raises(BeartypeSubscriptedIsInstantiationException):
        SubscriptedIs(
            is_valid=lambda text: bool(text),
            is_valid_code='',
            get_repr=lambda: f'Is[lambda text: bool(text)]',
        )

    # Assert that attempting to instantiate the "SubscriptedIs" class with
    # non-empty string code but *NO* code locals raises the expected exception.
    with raises(BeartypeSubscriptedIsInstantiationException):
        SubscriptedIs(
            is_valid=lambda text: bool(text),
            is_valid_code='Into the mouth of hell',
            get_repr=lambda: f'Is[lambda text: bool(text)]',
        )

    # Assert that attempting to instantiate the "SubscriptedIs" class with
    # non-empty string code and code locals such that that code does *NOT*
    # contain the test subject substring "{obj}" raises the expected exception.
    with raises(BeartypeSubscriptedIsInstantiationException):
        SubscriptedIs(
            is_valid=lambda text: bool(text),
            is_valid_code='Came through the jaws of Death,',
            is_valid_code_locals={},
            get_repr=lambda: f'Is[lambda text: bool(text)]',
        )

    # Assert that attempting to instantiate the "SubscriptedIs" class with
    # code locals but *NO* code raises the expected
    # exception.
    with raises(BeartypeSubscriptedIsInstantiationException):
        SubscriptedIs(
            is_valid=lambda text: bool(text),
            is_valid_code_locals={},
            get_repr=lambda: f'Is[lambda text: bool(text)]',
        )
