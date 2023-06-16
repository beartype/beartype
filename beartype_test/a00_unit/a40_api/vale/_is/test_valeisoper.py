#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype code-based operator data validation unit tests.**

This submodule unit tests the subset of the public API of the
:mod:`beartype.vale` subpackage defined by the private
:mod:`beartype.vale._is._valeisoper` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ class : isequal           }....................
def test_api_vale_isequal_pass() -> None:
    '''
    Test successful usage of the :mod:`beartype.vale.IsEqual` factory.
    '''

    # Defer test-specific imports.
    from beartype.vale import IsEqual
    from beartype.vale._core._valecore import BeartypeValidator

    # Arbitrary tuple objects with which to subscript the "IsEqual" class,
    # exercising edge cases in the __class_getitem__() dunder method.
    UNBODIED_JOY = ('Like an unbodied joy', 'whose race is just begun.')

    # Arbitrary hashable non-tuple objects with which to subscript the
    # "IsEqual" class, exercising edge cases in the __class_getitem__() dunder
    # method.
    KEEN_ARROWS = frozenset(
        {'Keen as are the arrows', 'Of that silver sphere,'})

    # Arbitrary non-tuple object we don't particularly care about.
    HARDLY_SEE = ['Until we hardly see,', 'we feel that it is there.']

    # Validator produced by subscripting the "IsEqual" class with exactly one
    # non-tuple object.
    IsUnbodiedJoy = IsEqual[UNBODIED_JOY]
    IsKeenArrows = IsEqual[KEEN_ARROWS]

    # Assert these validators satisfy the expected API.
    assert isinstance(IsUnbodiedJoy, BeartypeValidator)
    assert isinstance(IsKeenArrows, BeartypeValidator)

    # Assert these validators produce the same objects when subscripted by the
    # same arguments (and are thus memoized on subscripted arguments).
    assert IsUnbodiedJoy is IsEqual[UNBODIED_JOY]
    assert IsKeenArrows is IsEqual[KEEN_ARROWS]

    # Assert these validators accept the objects subscripting these validators.
    assert IsUnbodiedJoy.is_valid(UNBODIED_JOY) is True
    assert IsKeenArrows.is_valid(KEEN_ARROWS) is True

    # Assert these validators accept objects *NOT* subscripting these
    # validators but equal to the objects subscripting these validators.
    assert IsUnbodiedJoy.is_valid(UNBODIED_JOY[:]) is True
    assert IsKeenArrows.is_valid(KEEN_ARROWS.copy()) is True

    # Assert these validators reject objects unequal to the objects
    # subscripting these validators.
    assert IsUnbodiedJoy.is_valid(HARDLY_SEE) is False
    assert IsKeenArrows.is_valid(HARDLY_SEE) is False

    # Assert these validators have the expected representation.
    assert repr(UNBODIED_JOY) in repr(IsUnbodiedJoy)
    assert repr(KEEN_ARROWS) in repr(IsKeenArrows)

    # Validator synthesized from the above validators with the domain-specific
    # language (DSL) supported by these validators.
    IsUnbodiedJoyOrKeenArrows = IsUnbodiedJoy | IsKeenArrows

    # Assert this validator performs the expected validation.
    assert IsUnbodiedJoyOrKeenArrows.is_valid(UNBODIED_JOY[:]) is True
    assert IsUnbodiedJoyOrKeenArrows.is_valid(KEEN_ARROWS.copy()) is True
    assert IsUnbodiedJoyOrKeenArrows.is_valid(HARDLY_SEE) is False

    # Assert this validator provides the expected representation.
    assert '|' in repr(IsUnbodiedJoyOrKeenArrows)


def test_api_vale_isequal_fail() -> None:
    '''
    Test unsuccessful usage of the :mod:`beartype.vale.IsEqual` factory.
    '''

    # Defer test-specific imports.
    from beartype.roar import BeartypeValeSubscriptionException
    from beartype.vale import IsEqual
    from pytest import raises

    # Assert that subscripting the "IsEqual" class with the empty tuple raises
    # the expected exception.
    with raises(BeartypeValeSubscriptionException):
        IsEqual[()]
