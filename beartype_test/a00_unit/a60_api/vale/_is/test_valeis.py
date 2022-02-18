#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype callable-based data validation unit tests.**

This submodule unit tests the subset of the public API of the
:mod:`beartype.vale` subpackage defined by the private
:mod:`beartype.vale._is._valeis` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ class : is                }....................
def test_api_vale_is_pass() -> None:
    '''
    Test successful usage of the :mod:`beartype.vale.Is` factory.
    '''

    # Defer heavyweight imports.
    from beartype.vale import Is
    from beartype.vale._core._valecore import BeartypeValidator
    from collections.abc import Mapping

    def _is_quoted(text):
        '''
        Non-lambda function suitable for subscripting the
        :mod:`beartype.vale.Is` factory with.
        '''

        return '"' in text or "'" in text

    # Validators produced by subscripting this factory with lambda functions
    # satisfying the data validator API.
    IsLengthy = Is[lambda text: len(text) > 30]
    IsSentence = Is[lambda text: text and text[-1] == '.']

    # Validator produced by subscripting this factory with a non-lambda
    # function satisfying the data validator API.
    IsQuoted = Is[_is_quoted]

    # Assert these validators satisfy the expected API.
    assert isinstance(IsLengthy, BeartypeValidator)
    assert isinstance(IsSentence, BeartypeValidator)
    assert isinstance(IsQuoted, BeartypeValidator)

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

    # Assert an validator produced by subscripting this factory with a lambda
    # function satisfying the data validator API has the expected
    # representation.
    IsLengthyRepr = repr(IsLengthy)
    assert 'len(text) > 30' in IsLengthyRepr

    # Assert an validator produced by subscripting this factory with a
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
    IsLengthyOrUnquotedSentence_repr = repr(IsLengthyOrUnquotedSentence)
    assert '|' in IsLengthyOrUnquotedSentence_repr
    assert '&' in IsLengthyOrUnquotedSentence_repr
    assert '~' in IsLengthyOrUnquotedSentence_repr

    # Assert that this validator reports the expected diagnosis for a string
    # violating exactly one of the subvalidators composing this validator.
    IsLengthyOrUnquotedSentence_diagnosis = (
        IsLengthyOrUnquotedSentence.get_diagnosis(
            obj='For "the very spirit" fails.',
            indent_level_outer='    ',
            indent_level_inner='',
        ))
    assert IsLengthyOrUnquotedSentence_diagnosis.count('False') == 4
    assert IsLengthyOrUnquotedSentence_diagnosis.count('True') == 2
    assert '|' in IsLengthyOrUnquotedSentence_diagnosis
    assert '&' in IsLengthyOrUnquotedSentence_diagnosis
    assert '~' in IsLengthyOrUnquotedSentence_diagnosis



def test_api_vale_is_fail() -> None:
    '''
    Test unsuccessful usage of the :mod:`beartype.vale.Is` factory.
    '''

    # Defer heavyweight imports.
    from beartype.roar import BeartypeValeSubscriptionException
    from beartype.vale import Is
    from pytest import raises

    # Assert that subscripting this factory with the empty tuple raises the
    # expected exception.
    with raises(BeartypeValeSubscriptionException):
        Is[()]

    # Assert that subscripting this factory with two or more arguments raises
    # the expected exception.
    with raises(BeartypeValeSubscriptionException):
        Is['Cannon to right of them,', 'Cannon to left of them,']

    # Assert that subscripting this factory with a non-callable argument
    # raises the expected exception.
    with raises(BeartypeValeSubscriptionException):
        Is['Cannon in front of them']

    # Assert that subscripting this factory with a C-based callable argument
    # raises the expected exception.
    with raises(BeartypeValeSubscriptionException):
        Is[iter]

    # Assert that subscripting this factory with a pure-Python callable that
    # does *NOT* accept exactly one argument raises the expected exception.
    with raises(BeartypeValeSubscriptionException):
        Is[lambda: True]

    # Assert that subscripting this factory with a pure-Python callable that
    # does *NOT* accept exactly one argument raises the expected exception.
    with raises(BeartypeValeSubscriptionException):
        Is[lambda: True]

    # Object produced by subscripting this factory with a valid validator.
    IsNonEmpty = Is[lambda text: bool(text)]

    # Assert that attempting to synthesize new objects from the above object
    # with the domain-specific language (DSL) supported by that object and an
    # arbitrary object that is *NOT* an instance of the same class raises the
    # expected exception.
    with raises(BeartypeValeSubscriptionException):
        IsNonEmpty & 'While horse and hero fell.'
    with raises(BeartypeValeSubscriptionException):
        IsNonEmpty | 'While horse and hero fell.'

# ....................{ TESTS ~ decor                     }....................
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
    from beartype_test.util.mod.pytmodimport import (
        import_module_typing_any_attr_or_none_safe)
    from pytest import raises

    # "typing.Annotated" type hint factory imported from either the "typing" or
    # "typing_extensions" modules if importable *OR* "None" otherwise.
    Annotated = import_module_typing_any_attr_or_none_safe('Annotated')

    # If this factory is unimportable, the active Python interpreter fails to
    # support PEP 593. In this case, reduce to a noop.
    if Annotated is None:
        return
    # Else, this interpreter supports PEP 593.

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
