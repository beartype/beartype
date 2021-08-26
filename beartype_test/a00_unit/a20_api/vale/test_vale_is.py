#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype callable-based data validation unit tests.**

This submodule unit tests the subset of the public API of the
:mod:`beartype.vale` subpackage defined by the private
:mod:`beartype.vale._valeis` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype_test.util.mark.pytskip import skip_if_python_version_less_than
from pytest import raises

# ....................{ TESTS ~ class : is                }....................
@skip_if_python_version_less_than('3.7.0')
def test_api_vale_is_pass() -> None:
    '''
    Test successful usage of the public :mod:`beartype.vale.Is` class if the
    active Python interpreter targets Python >= 3.7 (and thus supports the
    ``__class_getitem__()`` dunder method) *or* skip otherwise.
    '''

    # Defer heavyweight imports.
    from beartype.vale import Is
    from beartype._vale._valesub import _SubscriptedIs
    from collections.abc import Mapping

    def _is_quoted(text):
        '''
        Non-lambda function satisfying the data validator API.
        '''

        return '"' in text or "'" in text

    # Validators produced by subscripting the "Is" class with lambda functions
    # satisfying the data validator API.
    IsLengthy = Is[lambda text: len(text) > 30]
    IsSentence = Is[lambda text: text and text[-1] == '.']

    # Validator produced by subscripting the "Is" class with a non-lambda
    # function satisfying the data validator API.
    IsQuoted = Is[_is_quoted]

    # Assert these validators satisfy the expected API.
    assert isinstance(IsLengthy, _SubscriptedIs)
    assert isinstance(IsSentence, _SubscriptedIs)
    assert isinstance(IsQuoted, _SubscriptedIs)

    # Assert these validators perform the expected validation.
    assert IsLengthy.is_valid('Plunged in the battery-smoke') is False
    assert IsLengthy.is_valid('Right through the line they broke;') is True
    assert IsSentence.is_valid('Theirs not to make reply,') is False
    assert IsSentence.is_valid('Theirs but to do and die.') is True
    assert IsQuoted.is_valid('Theirs not to reason why,') is False
    assert IsQuoted.is_valid('"Forward, the Light Brigade!"') is True

    # Assert one such validator provides both non-empty code and code locals.
    assert isinstance(IsLengthy._is_valid_code, str)
    assert isinstance(IsLengthy._is_valid_code_locals, Mapping)
    assert bool(IsLengthy._is_valid_code)
    assert bool(IsLengthy._is_valid_code_locals)

    # Assert an validator produced by subscripting the "Is" class with a lambda
    # function satisfying the data validator API has the expected
    # representation.
    IsLengthyRepr = repr(IsLengthy)
    assert 'len(text) > 30' in IsLengthyRepr

    # Assert an validator produced by subscripting the "Is" class with a
    # non-lambda function satisfying the data validator API has the expected
    # representation.
    IsQuotedRepr = repr(IsQuoted)
    assert '._is_quoted' in IsQuotedRepr

    # Assert that repeated accesses of that representation are memoized by
    # efficiently returning the same string.
    assert repr(IsLengthy) is IsLengthyRepr

    # Validator synthesized from the above validators with the domain-specific
    # language (DSL) supported by those validators.
    IsLengthyOrUnquotedSentence = IsLengthy | (IsSentence & ~IsQuoted)

    # Assert this validator performs the expected validation.
    assert IsLengthyOrUnquotedSentence.is_valid(
        'Stormed at with shot and shell,') is True
    assert IsLengthyOrUnquotedSentence.is_valid(
        'Rode the six hundred.') is True
    assert IsLengthyOrUnquotedSentence.is_valid(
        '"Forward, the Light Brigade.') is False
    assert IsLengthyOrUnquotedSentence.is_valid(
        'Into the valley of Death') is False

    # Assert this validator provides the expected representation.
    IsLengthyOrUnquotedSentenceRepr = repr(IsLengthyOrUnquotedSentence)
    assert '|' in IsLengthyOrUnquotedSentenceRepr
    assert '&' in IsLengthyOrUnquotedSentenceRepr
    assert '~' in IsLengthyOrUnquotedSentenceRepr


@skip_if_python_version_less_than('3.7.0')
def test_api_vale_is_fail() -> None:
    '''
    Test unsuccessful usage of the public :mod:`beartype.vale.Is` class if the
    active Python interpreter targets Python >= 3.7 (and thus supports the
    ``__class_getitem__()`` dunder method) *or* skip otherwise.
    '''

    # Defer heavyweight imports.
    from beartype.roar import BeartypeValeSubscriptionException
    from beartype.vale import Is

    # Assert that instantiating the "Is" class raises the expected exception.
    with raises(BeartypeValeSubscriptionException):
        Is()

    # Assert that subscripting the "Is" class with the empty tuple raises the
    # expected exception.
    with raises(BeartypeValeSubscriptionException):
        Is[()]

    # Assert that subscripting the "Is" class with two or more arguments raises
    # the expected exception.
    with raises(BeartypeValeSubscriptionException):
        Is['Cannon to right of them,', 'Cannon to left of them,']

    # Assert that subscripting the "Is" class with a non-callable argument
    # raises the expected exception.
    with raises(BeartypeValeSubscriptionException):
        Is['Cannon in front of them']

    # Assert that subscripting the "Is" class with a C-based callable argument
    # raises the expected exception.
    with raises(BeartypeValeSubscriptionException):
        Is[iter]

    # Assert that subscripting the "Is" class with a pure-Python callable that
    # does *NOT* accept exactly one argument raises the expected exception.
    with raises(BeartypeValeSubscriptionException):
        Is[lambda: True]

    # Assert that subscripting the "Is" class with a pure-Python callable that
    # does *NOT* accept exactly one argument raises the expected exception.
    with raises(BeartypeValeSubscriptionException):
        Is[lambda: True]

    # Object produced by subscripting the "Is" class with a valid validator.
    IsNonEmpty = Is[lambda text: bool(text)]

    # Assert that attempting to synthesize new objects from the above object
    # with the domain-specific language (DSL) supported by that object and an
    # arbitrary object that is *NOT* an instance of the same class raises the
    # expected exception.
    with raises(BeartypeValeSubscriptionException):
        IsNonEmpty & 'While horse and hero fell.'
    with raises(BeartypeValeSubscriptionException):
        IsNonEmpty | 'While horse and hero fell.'

# ....................{ TESTS ~ class : subscriptedis     }....................
@skip_if_python_version_less_than('3.7.0')
def test_api_vale_subscriptedis_pass() -> None:
    '''
    Test successful usage of the private
    :mod:`beartype._vale._valesub._SubscriptedIs` class if the active Python
    interpreter targets Python >= 3.7 (and thus supports the
    ``__class_getitem__()`` dunder method) *or* skip otherwise.
    '''

    # Defer heavyweight imports.
    from beartype._vale._valesub import _SubscriptedIs

    # Arbitrary valid data validator.
    not_though_the_soldier_knew = lambda text: bool('Someone had blundered.')

    # Keyword arguments passing arguments describing this validator excluding
    # the "get_repr" argument.
    kwargs_sans_get_repr = dict(
        is_valid=not_though_the_soldier_knew,
        is_valid_code_locals={'yum': not_though_the_soldier_knew},
    )

    # Keyword arguments passing arguments describing this validator including
    # the "get_repr" argument.
    kwargs = kwargs_sans_get_repr.copy()
    kwargs['get_repr'] = lambda: (
        "Is[lambda text: bool('Someone had blundered.')]")

    # Code already prefixed by "(" and suffixed by ")".
    is_valid_code_delimited = "({obj} == 'Was there a man dismayed?')"

    # Code *NOT* already prefixed by "(" and suffixed by ")".
    is_valid_code_undelimited = "{obj} == 'All in the valley of Death'"

    # Assert the "_SubscriptedIs" class preserves delimited code as is.
    subscriptedis_delimited = _SubscriptedIs(
        is_valid_code=is_valid_code_delimited, **kwargs)
    assert subscriptedis_delimited._is_valid_code is is_valid_code_delimited

    # Assert the "_SubscriptedIs" class delimits undelimited code.
    subscriptedis_undelimited = _SubscriptedIs(
        is_valid_code=is_valid_code_undelimited, **kwargs)
    assert (
        subscriptedis_undelimited._is_valid_code ==
        f'({is_valid_code_undelimited})'
    )

    # Assert that the "_SubscriptedIs" class also accepts a string representer.
    subscriptedis_repr_str = _SubscriptedIs(
        is_valid_code=is_valid_code_delimited,
        get_repr='All that was left of them,',
        **kwargs_sans_get_repr
    )

    # Assert these objects have the expected representations.
    assert 'Someone had blundered.' in repr(subscriptedis_delimited)
    assert repr(subscriptedis_repr_str) == 'All that was left of them,'



@skip_if_python_version_less_than('3.7.0')
def test_api_vale_subscriptedis_fail() -> None:
    '''
    Test unsuccessful usage of the private
    :mod:`beartype._vale._valesub._SubscriptedIs` class if the active Python
    interpreter targets Python >= 3.7 (and thus supports the
    ``__class_getitem__()`` dunder method) *or* skip otherwise.
    '''

    # Defer heavyweight imports.
    from beartype.roar import BeartypeValeSubscriptionException
    from beartype._vale._valesub import _SubscriptedIs

    # Arbitrary valid data validator.
    into_the_jaws_of_death = lambda text: bool('Into the mouth of hell')

    # Assert that attempting to instantiate the "_SubscriptedIs" class with
    # non-string code raises the expected exception.
    with raises(BeartypeValeSubscriptionException):
        _SubscriptedIs(
            is_valid=into_the_jaws_of_death,
            is_valid_code=b'Into the jaws of Death,',
            is_valid_code_locals={'yum': into_the_jaws_of_death},
            get_repr=lambda: "Is[lambda text: bool('Into the mouth of hell')]",
        )

    # Assert that attempting to instantiate the "_SubscriptedIs" class with
    # empty code raises the expected exception.
    with raises(BeartypeValeSubscriptionException):
        _SubscriptedIs(
            is_valid=into_the_jaws_of_death,
            is_valid_code='',
            is_valid_code_locals={'yum': into_the_jaws_of_death},
            get_repr=lambda: "Is[lambda text: bool('Into the mouth of hell')]",
        )

    # Assert that attempting to instantiate the "_SubscriptedIs" class with code
    # *NOT* containing the substring "{obj}" raises the expected exception.
    with raises(BeartypeValeSubscriptionException):
        _SubscriptedIs(
            is_valid=into_the_jaws_of_death,
            is_valid_code='Came through the jaws of Death,',
            is_valid_code_locals={'yum': into_the_jaws_of_death},
            get_repr=lambda: "Is[lambda text: bool('Into the mouth of hell')]",
        )

    # Assert that attempting to instantiate the "_SubscriptedIs" class with
    # valid code and non-dictionary code locals raises the expected exception.
    with raises(BeartypeValeSubscriptionException):
        _SubscriptedIs(
            is_valid=into_the_jaws_of_death,
            is_valid_code="{obj} == 'Back from the mouth of hell,'",
            is_valid_code_locals={'yum', into_the_jaws_of_death},
            get_repr=lambda: "Is[lambda text: bool('Into the mouth of hell')]",
        )

    # Keyword arguments passing valid code and non-dictionary code locals.
    kwargs_good = dict(
        is_valid=into_the_jaws_of_death,
        is_valid_code="{obj} == 'Back from the mouth of hell,'",
        is_valid_code_locals={'yum': into_the_jaws_of_death},
    )

    # Assert that attempting to instantiate the "_SubscriptedIs" class with
    # valid code and code locals but an invalid representer raises the
    # expected exception.
    with raises(BeartypeValeSubscriptionException):
        _SubscriptedIs(get_repr=b'All that was left of them,', **kwargs_good)

    # Assert that attempting to instantiate the "_SubscriptedIs" class with
    # valid code and code locals but a C-based representer raises the expected
    # exception.
    with raises(BeartypeValeSubscriptionException):
        _SubscriptedIs(get_repr=iter, **kwargs_good)

    # Assert that attempting to instantiate the "_SubscriptedIs" class with
    # valid code and code locals but a pure-Python representer accepting one or
    # more arguments raises the expected exception.
    with raises(BeartypeValeSubscriptionException):
        _SubscriptedIs(
            get_repr=lambda rode, the, six, hundred:
                'Into the valley of Death',
            **kwargs_good
        )

# ....................{ TESTS ~ decor                     }....................
@skip_if_python_version_less_than('3.9.0')
def test_api_vale_decor_fail() -> None:
    '''
    Test unsuccessful usage of the public :mod:`beartype.vale.Is` class when
    used to type hint callables decorated by the :func:`beartype.beartype`
    decorator if the active Python interpreter targets Python >= 3.9 (and thus
    supports the :class:`typing.Annotated` class required to do so) *or* skip
    otherwise.
    '''

    # Defer heavyweight imports.
    from beartype import beartype
    from beartype.roar import BeartypeDecorHintPep593Exception
    from beartype.vale import Is
    from typing import Annotated

    # Assert that @beartype raises the expected exception when decorating a
    # callable annotated by a type metahint whose first argument is a
    # beartype-specific data validator and whose second argument is a
    # beartype-agnostic object.
    with raises(BeartypeDecorHintPep593Exception):
        @beartype
        def volleyed_and_thundered(
            flashed_all_their_sabres_bare: Annotated[
                str,
                Is[lambda text: bool('Flashed as they turned in air')],
                'Sabring the gunners there,',
            ]
        ) -> str:
            return flashed_all_their_sabres_bare + 'Charging an army, while'
