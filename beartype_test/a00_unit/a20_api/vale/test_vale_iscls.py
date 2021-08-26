#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype code-based type data validation unit tests.**

This submodule unit tests the subset of the public API of the
:mod:`beartype.vale` subpackage defined by the private
:mod:`beartype.vale._valeiscls` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype_test.util.mark.pytskip import skip_if_python_version_less_than

# ....................{ TESTS ~ class : issubclass        }....................
@skip_if_python_version_less_than('3.7.0')
def test_api_vale_issubclass_pass() -> None:
    '''
    Test successful usage of the public :mod:`beartype.vale.IsSubclass` class
    if the active Python interpreter targets Python >= 3.7 (and thus supports
    the ``__class_getitem__()`` dunder method) *or* skip otherwise.
    '''

    # Defer heavyweight imports.
    from beartype.vale import IsSubclass
    from beartype._util.utilobject import get_object_name
    from beartype._vale._valesub import _SubscriptedIs
    from beartype_test.a00_unit.data.data_type import (
        Class, Subclass, SubclassSubclass)

    # Validator produced by subscripting the "IsSubclass" class with exactly
    # one superclass.
    IsClassSubclass = IsSubclass[Class]
    IsSubclassSubclass = IsSubclass[Subclass]

    # Assert these validators satisfy the expected API.
    assert isinstance(IsClassSubclass, _SubscriptedIs)
    assert isinstance(IsSubclassSubclass, _SubscriptedIs)

    # Assert these validators produce the same objects when subscripted by the
    # same arguments (and are thus memoized on subscripted arguments).
    assert IsClassSubclass is IsSubclass[Class]
    assert IsSubclassSubclass is IsSubclass[Subclass]

    # Assert these validators accept the superclasses subscripting these
    # validators. By definition, any class is a subclass of itself.
    assert IsClassSubclass.is_valid(Class) is True
    assert IsSubclassSubclass.is_valid(Subclass) is True

    # Assert these validators accept subclasses of the superclasses
    # subscripting these validators.
    assert IsClassSubclass.is_valid(Subclass) is True
    assert IsSubclassSubclass.is_valid(SubclassSubclass) is True

    # Assert these validators reject classes *NOT* subclassing the superclasses
    # subscripting these validators.
    assert IsClassSubclass.is_valid(type) is False
    assert IsSubclassSubclass.is_valid(Class) is False

    # Assert these validators reject non-classes.
    assert IsClassSubclass.is_valid(
        'Over whose pines, and crags, and caverns sail') is False
    assert IsSubclassSubclass.is_valid(
        'Fast cloud-shadows and sunbeams: awful scene,') is False

    # Assert these validators have the expected representation.
    assert get_object_name(Class) in repr(IsClassSubclass)
    assert get_object_name(Subclass) in repr(IsSubclassSubclass)

    # Validator synthesized from the above validators with the domain-specific
    # language (DSL) supported by these validators.
    IsSubclassExcessive = IsSubclassSubclass | IsClassSubclass

    # Assert this validator performs the expected validation.
    assert IsSubclassExcessive.is_valid(Class) is True
    assert IsSubclassExcessive.is_valid(Subclass) is True
    assert IsSubclassExcessive.is_valid(SubclassSubclass) is True

    # Assert this validator provides the expected representation.
    assert '|' in repr(IsSubclassExcessive)


@skip_if_python_version_less_than('3.7.0')
def test_api_vale_issubclass_fail() -> None:
    '''
    Test unsuccessful usage of the public :mod:`beartype.vale.IsSubclass` class
    if the active Python interpreter targets Python >= 3.7 (and thus supports
    the ``__class_getitem__()`` dunder method) *or* skip otherwise.
    '''

    # Defer heavyweight imports.
    from beartype.roar import BeartypeValeSubscriptionException
    from beartype.vale import IsSubclass
    from beartype_test.a00_unit.data.data_type import NonIssubclassableClass
    from pytest import raises

    # Assert that instantiating the "IsSubclass" class raises the expected
    # exception.
    with raises(BeartypeValeSubscriptionException):
        IsSubclass()

    # Assert that subscripting the "IsSubclass" class with the empty tuple
    # raises the expected exception.
    with raises(BeartypeValeSubscriptionException):
        IsSubclass[()]

    # Assert that subscripting the "IsSubclass" class with a non-class raises
    # the expected exception.
    with raises(BeartypeValeSubscriptionException):
        IsSubclass['Where Power in likeness of the Arve comes down']

    # Assert that subscripting the "IsSubclass" class with a non-issubclassable
    # class raises the expected exception.
    with raises(BeartypeValeSubscriptionException):
        IsSubclass[NonIssubclassableClass]
