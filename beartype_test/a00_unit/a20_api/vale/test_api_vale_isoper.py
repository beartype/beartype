#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype code-based operator data validation unit tests.**

This submodule unit tests the subset of the public API of the
:mod:`beartype.vale` subpackage defined by the private
:mod:`beartype.vale._valeisoper` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype_test.util.mark.pytskip import skip_if_python_version_less_than
from pytest import raises

# ....................{ TESTS ~ class : isequal           }....................
@skip_if_python_version_less_than('3.7.0')
def test_api_vale_isequal_pass() -> None:
    '''
    Test successful usage of the public :mod:`beartype.vale.IsEqual` class if
    the active Python interpreter targets Python >= 3.7 (and thus supports the
    ``__class_getitem__()`` dunder method) *or* skip otherwise.
    '''

    # Defer heavyweight imports.
    from beartype.vale import IsEqual
    from beartype.vale._valeissub import _SubscriptedIs
    from collections.abc import Mapping

    # Arbitrary tuple objects with which to subscript the "IsEqual" class,
    # exercising edge cases in the __class_getitem__() dunder method.
    UNBODIED_JOY = ('Like an unbodied joy', 'whose race is just begun.')

    # Arbitrary non-tuple objects with which to subscript the "IsEqual" class,
    # exercising edge cases in the __class_getitem__() dunder method.
    KEEN_ARROWS = ['Keen as are the arrows', 'Of that silver sphere,']
    HARDLY_SEE = ['Until we hardly see,', 'we feel that it is there.']

    # Validator produced by subscripting the "IsEqual" class with exactly one
    # non-tuple object.
    IsUnbodiedJoy = IsEqual[UNBODIED_JOY]
    IsKeenArrows = IsEqual[KEEN_ARROWS]

    # Assert this validator satisfies the expected API.
    assert isinstance(IsUnbodiedJoy, _SubscriptedIs)

    # Assert this validator accepts the object subscripting this validator.
    assert IsUnbodiedJoy.is_valid(UNBODIED_JOY) is True
    assert IsKeenArrows.is_valid(KEEN_ARROWS) is True

    # Assert this validator accepts objects *NOT* subscripting this validator
    # but still equal to the object subscripting this validator.
    assert IsUnbodiedJoy.is_valid(UNBODIED_JOY[:]) is True
    assert IsKeenArrows.is_valid(KEEN_ARROWS[:]) is True

    # Assert this validator rejects objects unequal to the object subscripting
    # this validator.
    assert IsUnbodiedJoy.is_valid(HARDLY_SEE) is False
    assert IsKeenArrows.is_valid(HARDLY_SEE) is False

    # Assert this validator provides both non-empty code and code locals.
    assert isinstance(IsUnbodiedJoy._is_valid_code, str)
    assert isinstance(IsUnbodiedJoy._is_valid_code_locals, Mapping)
    assert bool(IsUnbodiedJoy._is_valid_code)
    assert bool(IsUnbodiedJoy._is_valid_code_locals)

    # Assert this validator has the expected representation.
    assert repr(UNBODIED_JOY) in repr(IsUnbodiedJoy)

    # Validator synthesized from the above validators with the domain-specific
    # language (DSL) supported by those validators.
    IsUnbodiedJoyOrKeenArrows = IsUnbodiedJoy | IsKeenArrows

    # Assert this object performs the expected validation.
    assert IsUnbodiedJoyOrKeenArrows.is_valid(UNBODIED_JOY[:]) is True
    assert IsUnbodiedJoyOrKeenArrows.is_valid(KEEN_ARROWS[:]) is True
    assert IsUnbodiedJoyOrKeenArrows.is_valid(HARDLY_SEE) is False

    # Assert this object provides the expected representation.
    assert '|' in repr(IsUnbodiedJoyOrKeenArrows)


@skip_if_python_version_less_than('3.7.0')
def test_api_vale_isequal_fail() -> None:
    '''
    Test unsuccessful usage of the public :mod:`beartype.vale.IsEqual` class if
    the active Python interpreter targets Python >= 3.7 (and thus supports the
    ``__class_getitem__()`` dunder method) *or* skip otherwise.
    '''

    # Defer heavyweight imports.
    from beartype.roar import BeartypeValeSubscriptionException
    from beartype.vale import IsEqual

    # Assert that instantiating the "IsEqual" class raises the expected
    # exception.
    with raises(BeartypeValeSubscriptionException):
        IsEqual()

    # Assert that subscripting the "IsEqual" class with the empty tuple raises
    # the expected exception.
    with raises(BeartypeValeSubscriptionException):
        IsEqual[()]
