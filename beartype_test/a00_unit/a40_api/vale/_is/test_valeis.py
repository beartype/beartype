#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype callable-based data validation unit tests.**

This submodule unit tests the subset of the public API of the
:mod:`beartype.vale` subpackage defined by the private
:mod:`beartype.vale._is._valeis` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ class : is                 }....................
def test_api_vale_is_pass() -> None:
    '''
    Test successful usage of the :mod:`beartype.vale.Is` factory.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype import beartype
    from beartype._util.func.utilfuncmake import make_func
    from beartype.vale import Is
    from beartype.vale._core._valecore import BeartypeValidator
    from collections.abc import Mapping

    # ....................{ CLASSES                        }....................
    class FalseFake(object):
        '''
        Arbitrary class whose instances are implicitly convertible into
        **booleans** (i.e., :class:`bool` objects) via the :meth:`__bool__`
        dunder method despite *not* subclassing the builtin :class:`bool` type.
        '''

        def __bool__(self) -> bool:
            '''
            Dunder method coercing this non-boolean into a boolean.
            '''

            # Return false rather than true to exercise a non-trivial edge case
            # in which the callable subscripting an "Is[...]" validator returns
            # a non-boolean object, which then induces a validation failure,
            # which then displays a validator diagnosis embedding that object.
            return False

    # ....................{ FUNCS                          }....................
    # Undecorated non-lambda function with which to subscript the "Is" factory.
    def _is_quoted(text):
        return '"' in text or "'" in text

    # Undecorated non-lambda function returning a non-boolean object implicitly
    # convertible into a boolean with which to subscript the "Is" factory,
    # exercising an edge case coercing the former to the latter in that factory.
    def _is_false_fake(obj):
        return FalseFake()

    # Decorated non-lambda function with which to subscript the "Is" factory,
    # exercising an edge case validating callable parameters in that factory.
    @beartype
    def _is_exclamatory(text: str):
        return '!' in text

    # Dynamically generated lambda function. To exercise in-memory validators
    # dynamically defined outside of a standard on-disk module (e.g., "smart"
    # REPLs like IPython), this function's code is intentionally cached with
    # the standard "linecache" module.
    _is_commentary = make_func(
        func_name='_is_commentary',
        func_code=(
            """_is_commentary = lambda text: text and text[-1] == ','"""),
        is_debug=True,
    )

    # ....................{ VALIDATORS                     }....................
    # Validators produced by subscripting this factory with lambda functions
    # satisfying the expected API defined physically in this on-disk module.
    IsLengthy = Is[lambda text: len(text) > 30]
    IsSentence = Is[lambda text: text and text[-1] == '.']

    # Validators produced by subscripting this factory with lambda functions
    # satisfying the expected API defined dynamically in-memory.
    IsCommentary = Is[_is_commentary]

    # Validator produced by subscripting this factory with non-lambda functions
    # satisfying the expected API.
    IsQuoted = Is[_is_quoted]
    IsExclamatory = Is[_is_exclamatory]
    IsFalseFake = Is[_is_false_fake]

    # Validator synthesized from the above validators with the domain-specific
    # language (DSL) supported by those validators.
    IsLengthyOrUnquotedSentence = IsLengthy | (IsSentence & ~IsQuoted)

    # ....................{ ASSERTS ~ instance             }....................
    # Assert these validators satisfy the expected API.
    assert isinstance(IsLengthy, BeartypeValidator)
    assert isinstance(IsLengthyOrUnquotedSentence, BeartypeValidator)

    # Assert a validator provides both non-empty code and code locals.
    assert isinstance(IsLengthy._is_valid_code, str)
    assert isinstance(IsLengthy._is_valid_code_locals, Mapping)
    assert bool(IsLengthy._is_valid_code)
    assert bool(IsLengthy._is_valid_code_locals)

    # ....................{ ASSERTS ~ is_valid             }....................
    # Assert that non-composite validators perform the expected validation.
    assert IsLengthy.is_valid('Plunged in the battery-smoke') is False
    assert IsLengthy.is_valid('Right through the line they broke;') is True
    assert IsSentence.is_valid('Theirs not to make reply,') is False
    assert IsSentence.is_valid('Theirs but to do and die.') is True
    assert IsCommentary.is_valid('Remote, serene, and inaccessible:') is False
    assert IsCommentary.is_valid(
        'Power dwells apart in its tranquillity,') is True
    assert IsQuoted.is_valid('Theirs not to reason why,') is False
    assert IsQuoted.is_valid('"Forward, the Light Brigade!"') is True
    assert IsExclamatory.is_valid(
        'Thou art the path of that unresting sound—') is False
    assert IsExclamatory.is_valid(
        '"Dizzy Ravine! and when I gaze on thee"') is True

    # Assert that a composite validator performs the expected validation.
    assert IsLengthyOrUnquotedSentence.is_valid(
        'Stormed at with shot and shell,') is True
    assert IsLengthyOrUnquotedSentence.is_valid(
        'Rode the six hundred.') is True
    assert IsLengthyOrUnquotedSentence.is_valid(
        '"Forward, the Light Brigade.') is False
    assert IsLengthyOrUnquotedSentence.is_valid(
        'Into the valley of Death') is False

    # ....................{ ASSERTS ~ repr                 }....................
    # Assert a physical lambda-based validator has the expected representation.
    IsLengthyRepr = repr(IsLengthy)
    assert 'len(text) > 30' in IsLengthyRepr

    # Assert a dynamic lambda-based validator has the expected representation.
    IsCommentary = repr(IsCommentary)
    assert "text[-1] == ','" in IsCommentary

    # Assert a non-lambda-based validator has the expected representation.
    IsQuotedRepr = repr(IsQuoted)
    assert '._is_quoted' in IsQuotedRepr

    # Assert that repeated accesses of that representation are memoized by
    # efficiently returning the same string.
    assert repr(IsLengthy) is IsLengthyRepr

    # Assert this validator provides the expected representation.
    IsLengthyOrUnquotedSentence_repr = repr(IsLengthyOrUnquotedSentence)
    assert '|' in IsLengthyOrUnquotedSentence_repr
    assert '&' in IsLengthyOrUnquotedSentence_repr
    assert '~' in IsLengthyOrUnquotedSentence_repr

    # ....................{ ASSERTS ~ diagnosis            }....................
    # Assert that a composite validator reports the expected diagnosis for a
    # string violating one of the subvalidators composing this validator.
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

    # Assert that a non-composite validator subscripted by a callable returning
    # a non-boolean implicitly convertible into boolean "False" reports the
    # expected diagnosis for any arbitrary object.
    IsFalseFake_diagnosis = IsFalseFake.get_diagnosis(
        obj="Shine in the rushing torrents' restless gleam,",
        indent_level_outer='    ',
        indent_level_inner='',
    )
    assert IsFalseFake_diagnosis.count('False') == 1


def test_api_vale_is_fail() -> None:
    '''
    Test unsuccessful usage of the :mod:`beartype.vale.Is` factory.
    '''

    # Defer test-specific imports.
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

# ....................{ TESTS ~ decor                      }....................
def test_api_vale_decor_fail() -> None:
    '''
    Test unsuccessful usage of the public :mod:`beartype.vale.Is` class when
    used to type hint callables decorated by the :func:`beartype.beartype`
    decorator if the active Python interpreter targets Python >= 3.9 (and thus
    supports the :class:`typing.Annotated` class required to do so) *or* skip
    otherwise.
    '''

    # Defer test-specific imports.
    from beartype import beartype
    from beartype.roar import BeartypeDecorHintPep593Exception
    from beartype.vale import Is
    from beartype_test._util.module.pytmodtyping import (
        import_typing_attr_or_none_safe)
    from pytest import raises

    # "typing.Annotated" type hint factory imported from either the "typing" or
    # "typing_extensions" modules if importable *OR* "None" otherwise.
    Annotated = import_typing_attr_or_none_safe('Annotated')

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
